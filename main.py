#!/usr/bin/env python3
"""
Password Strength Checker CLI
A production-ready command-line utility for comprehensive password security evaluation.

Features:
- Shannon entropy and complexity scoring
- Dictionary word and pattern detection via zxcvbn
- HaveIBeenPwned API integration with k-Anonymity protocol
- Rich terminal UI with colored output
- Actionable security recommendations

Security Best Practices:
- Passwords never logged or stored
- HaveIBeenPwned checks use k-Anonymity (SHA-1 hashing, 5-char prefix only)
- Secure hidden input via getpass module
"""

import hashlib
import math
import re
import sys
from contextlib import contextmanager
from typing import Dict, List, Tuple
from collections import Counter

from urllib import error as urllib_error
from urllib import request as urllib_request
from getpass import getpass

try:
    from rich.console import Console  # type: ignore[reportMissingImports]
    from rich.table import Table  # type: ignore[reportMissingImports]
    from rich.panel import Panel  # type: ignore[reportMissingImports]
except ImportError:
    class Console:
        """Minimal fallback used when the optional Rich package is unavailable."""

        _markup = re.compile(r"\[/?[a-zA-Z_ ]+\]")

        def print(self, *objects, **kwargs):
            text = " ".join(str(obj) for obj in objects)
            print(self._markup.sub("", text))

        @contextmanager
        def status(self, message):
            self.print(message)
            yield

    class Panel:
        def __init__(self, renderable, **kwargs):
            self.renderable = renderable

        def __str__(self):
            return str(self.renderable)

    class Table:
        def __init__(self, title=None, **kwargs):
            self.title = title
            self.rows = []

        def add_column(self, *args, **kwargs):
            pass

        def add_row(self, *values, **kwargs):
            self.rows.append(values)

        def __str__(self):
            heading = f"{self.title}\n" if self.title else ""
            return heading + "\n".join(" | ".join(map(str, row)) for row in self.rows)

try:
    from zxcvbn import zxcvbn  # type: ignore[reportMissingModuleSource]
except ImportError:
    print("ERROR: zxcvbn not found. Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)


class PasswordStrengthChecker:
    """Main password evaluation engine."""
    
    def __init__(self):
        self.console = Console()
        self.password = None
        self.results = {}
        self.recommendations = []
        
    def get_password_input(self) -> str:
        """Securely prompt for password without echoing to terminal."""
        while True:
            password = getpass("Enter password to check (hidden): ")
            if not password:
                self.console.print("[yellow]⚠️  Password cannot be empty. Try again.[/yellow]")
                continue
            
            if len(password) > 256:
                self.console.print("[yellow]⚠️  Password exceeds 256 characters. Try again.[/yellow]")
                continue
                
            return password
    
    # ===== ENTROPY & COMPLEXITY ANALYSIS =====
    
    def calculate_entropy(self, password: str) -> float:
        """
        Calculate Shannon entropy: H = -Σ(p_i * log2(p_i))
        Measures password randomness based on character frequency.
        
        Args:
            password: The password to analyze
            
        Returns:
            Shannon entropy value in bits
        """
        if not password:
            return 0.0
        
        counter = Counter(password)
        entropy = 0.0
        
        for count in counter.values():
            probability = count / len(password)
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def get_character_pools(self, password: str) -> Dict[str, bool]:
        """
        Identify character classes present in password.
        
        Args:
            password: The password to analyze
            
        Returns:
            Dictionary with boolean flags for each character class
        """
        return {
            "lowercase": bool(re.search(r"[a-z]", password)),
            "uppercase": bool(re.search(r"[A-Z]", password)),
            "digits": bool(re.search(r"\d", password)),
            "special": bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};:'\",.<>?/\\|`~]", password)),
        }
    
    def calculate_complexity_score(self, password: str) -> Tuple[int, int]:
        """
        Calculate complexity score based on:
        - Character diversity (4 possible types)
        - Character count
        
        Args:
            password: The password to analyze
            
        Returns:
            Tuple of (current_score, max_possible_score)
        """
        max_score = 50  # Baseline max
        current_score = 0
        
        # Length scoring (0-20 points)
        length_score = min(len(password) // 2, 20)
        current_score += length_score
        
        # Character diversity scoring (0-30 points)
        char_pools = self.get_character_pools(password)
        diversity_score = sum(char_pools.values()) * 7.5  # 7.5 points per unique type (max 30)
        current_score += diversity_score
        
        return int(current_score), max_score
    
    # ===== ZXCVBN PATTERN DETECTION =====
    
    def analyze_zxcvbn(self, password: str) -> Dict:
        """
        Use zxcvbn to detect dictionary words, spatial patterns, sequences, repeats.
        
        Args:
            password: The password to analyze
            
        Returns:
            Dictionary with zxcvbn analysis results
        """
        try:
            result = zxcvbn(password)
            return {
                "score": result["score"],  # 0-4 (0=weak, 4=strong)
                "crack_times": result["crack_times_display"],
                "feedback": result["feedback"],
                "sequences": result["sequence"],
                "estimates": result["crack_times_display"],
            }
        except Exception as e:
            self.console.print(f"[red]Error during zxcvbn analysis: {e}[/red]")
            return {"score": 2, "feedback": {"warning": "Analysis unavailable"}}
    
    # ===== HAVEIBEENPWNED API (K-ANONYMITY) =====
    
    def check_haveibeenpwned(self, password: str) -> Tuple[bool, str]:
        """
        Check if password exists in HaveIBeenPwned breach database using k-Anonymity.
        
        Protocol (k-Anonymity):
        1. Hash password with SHA-1
        2. Send ONLY first 5 hex characters to API
        3. API returns all hashes starting with those 5 chars (k-set)
        4. Check locally if full hash exists in k-set
        
        This ensures the cleartext password NEVER leaves the client machine.
        
        Args:
            password: The password to check
            
        Returns:
            Tuple of (is_leaked: bool, message: str)
        """
        try:
            # Step 1: SHA-1 hash the password
            sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
            
            # Step 2: Split hash into prefix (first 5 chars) and suffix
            prefix = sha1_hash[:5]
            suffix = sha1_hash[5:]
            
            # Step 3: Query HaveIBeenPwned API with prefix only
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            headers = {"User-Agent": "PasswordStrengthChecker/1.0"}
            
            api_request = urllib_request.Request(url, headers=headers)
            with urllib_request.urlopen(api_request, timeout=5) as response:
                response_text = response.read().decode("utf-8")
            
            # Step 4: Parse response and check for full hash match locally
            for line in response_text.splitlines():
                if line:
                    response_suffix, count = line.split(":")
                    if response_suffix == suffix:
                        return True, f"⚠️  Password found in {count} breaches!"
            
            return False, "✓ Password not found in known breaches"
            
        except urllib_error.URLError as error:
            if isinstance(error.reason, TimeoutError):
                return None, "⏱️  API timeout (unable to verify)"
            return None, "🔌 No internet connection (unable to verify)"
        except TimeoutError:
            return None, "⏱️  API timeout (unable to verify)"
        except Exception as e:
            return None, f"⚠️  Verification error: {str(e)}"
    
    # ===== RECOMMENDATIONS ENGINE =====
    
    def generate_recommendations(self, password: str, zxcvbn_result: Dict) -> List[str]:
        """
        Generate specific, actionable improvement recommendations.
        
        Args:
            password: The password analyzed
            zxcvbn_result: Result from zxcvbn analysis
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        char_pools = self.get_character_pools(password)
        
        # Length recommendations
        if len(password) < 8:
            recommendations.append("🔧 Increase length to at least 8 characters (12+ recommended)")
        elif len(password) < 12:
            recommendations.append("🔧 Consider extending to 12+ characters for better strength")
        
        # Complexity recommendations
        if not char_pools["uppercase"]:
            recommendations.append("🔧 Add UPPERCASE letters")
        if not char_pools["lowercase"]:
            recommendations.append("🔧 Add lowercase letters")
        if not char_pools["digits"]:
            recommendations.append("🔧 Add numbers (0-9)")
        if not char_pools["special"]:
            recommendations.append("🔧 Add special characters (!@#$%^&*)")
        
        # zxcvbn feedback
        feedback = zxcvbn_result.get("feedback", {})
        if feedback.get("warning"):
            recommendations.append(f"🔧 {feedback['warning']}")
        
        if feedback.get("suggestions"):
            for suggestion in feedback["suggestions"][:2]:  # Limit to top 2
                recommendations.append(f"🔧 {suggestion}")
        
        # Pattern recommendations
        sequences = zxcvbn_result.get("sequences", [])
        if sequences:
            pattern_types = [seq.get("pattern", "unknown") for seq in sequences[:3]]
            recommendations.append(f"🔧 Avoid patterns: {', '.join(set(pattern_types))}")
        
        if not recommendations:
            recommendations.append("✓ No specific improvements needed!")
        
        return recommendations
    
    # ===== STRENGTH RATING =====
    
    def get_strength_rating(self, zxcvbn_score: int, leaked: bool) -> Tuple[str, str, str]:
        """
        Determine overall strength rating and color coding.
        
        Args:
            zxcvbn_score: Score from zxcvbn (0-4)
            leaked: Whether password found in breaches
            
        Returns:
            Tuple of (rating_text, color, emoji)
        """
        if leaked is True:
            return "COMPROMISED", "red", "🚨"
        
        score_mapping = {
            0: ("Very Weak", "red", "🔴"),
            1: ("Weak", "red", "🔴"),
            2: ("Fair", "yellow", "🟡"),
            3: ("Strong", "green", "🟢"),
            4: ("Very Strong", "bright_green", "🟢"),
        }
        return score_mapping.get(zxcvbn_score, ("Unknown", "white", "❓"))
    
    # ===== DISPLAY FUNCTIONS =====
    
    def display_results(self):
        """Format and display comprehensive analysis report."""
        if not self.results:
            self.console.print("[red]No analysis results available[/red]")
            return
        
        # Header
        self.console.print("\n")
        self.console.print(
            Panel(
                "[bold cyan]Password Strength Analysis Report[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
            )
        )
        
        # Strength Rating
        strength_text, color, emoji = self.results["strength"]
        self.console.print(
            f"\n[bold]Overall Strength:[/bold] [{color}]{emoji} {strength_text}[/{color}]"
        )
        
        # Metrics Table
        metrics_table = Table(title="📊 Security Metrics", show_header=True, header_style="bold cyan")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")
        
        metrics_table.add_row("Length", f"{len(self.password)} characters")
        metrics_table.add_row("Shannon Entropy", f"{self.results['entropy']:.2f} bits")
        metrics_table.add_row("Complexity Score", f"{self.results['complexity']}/50")
        
        char_pools = self.get_character_pools(self.password)
        charset_text = " + ".join([k for k, v in char_pools.items() if v])
        metrics_table.add_row("Character Types", charset_text or "None")
        
        self.console.print(metrics_table)
        
        # Pattern Analysis
        self.console.print("\n[bold cyan]Pattern Analysis (zxcvbn):[/bold cyan]")
        patterns = self.results.get("patterns", {})
        if patterns.get("sequences"):
            for i, seq in enumerate(patterns["sequences"][:3], 1):
                pattern_type = seq.get("pattern", "unknown").upper()
                self.console.print(f"  {i}. Detected: {pattern_type}")
        else:
            self.console.print("  ✓ No common patterns detected")
        
        # Breach Check
        self.console.print(f"\n[bold cyan]Breach Database Check:[/bold cyan]")
        breach_msg = self.results["breach_message"]
        breach_status = self.results["breach_status"]
        
        if breach_status is True:
            self.console.print(f"  [{color}]{breach_msg}[/{color}]")
        elif breach_status is False:
            self.console.print(f"  [green]{breach_msg}[/green]")
        else:
            self.console.print(f"  [yellow]{breach_msg}[/yellow]")
        
        # Recommendations
        self.console.print(f"\n[bold cyan]Recommendations:[/bold cyan]")
        if self.recommendations:
            for rec in self.recommendations:
                self.console.print(f"  {rec}")
        else:
            self.console.print("  ✓ No improvements suggested")
        
        # Estimated crack times
        crack_times = self.results.get("crack_times", {})
        if crack_times:
            self.console.print(f"\n[bold cyan]Estimated Crack Times:[/bold cyan]")
            self.console.print(f"  Online Attack: {crack_times.get('online_throttling_100_per_hour', 'N/A')}")
            self.console.print(f"  Offline Attack: {crack_times.get('offline_slow_hashing_1e4_per_second', 'N/A')}")
            self.console.print(f"  Offline Fast Attack: {crack_times.get('offline_fast_hashing_1e10_per_second', 'N/A')}")
        
        self.console.print("\n")
    
    # ===== MAIN ANALYSIS WORKFLOW =====
    
    def analyze(self, password: str = None) -> bool:
        """
        Execute complete password analysis pipeline.
        
        Args:
            password: Optional password (if None, prompts user)
            
        Returns:
            True if analysis successful, False otherwise
        """
        self.password = password or self.get_password_input()
        
        try:
            self.console.print("\n[cyan]🔍 Analyzing password...[/cyan]")
            
            # 1. Entropy calculation
            with self.console.status("[bold cyan]Calculating entropy..."):
                entropy = self.calculate_entropy(self.password)
            
            # 2. Complexity scoring
            with self.console.status("[bold cyan]Assessing complexity..."):
                complexity_score, max_complexity = self.calculate_complexity_score(self.password)
            
            # 3. Pattern detection via zxcvbn
            with self.console.status("[bold cyan]Scanning for patterns..."):
                zxcvbn_result = self.analyze_zxcvbn(self.password)
            
            # 4. Breach database check (k-Anonymity)
            with self.console.status("[bold cyan]Checking breach database (k-Anonymity)..."):
                is_leaked, breach_message = self.check_haveibeenpwned(self.password)
            
            # 5. Generate recommendations
            self.recommendations = self.generate_recommendations(self.password, zxcvbn_result)
            
            # 6. Determine strength rating
            strength_rating = self.get_strength_rating(zxcvbn_result["score"], is_leaked)
            
            # Store results
            self.results = {
                "entropy": entropy,
                "complexity": complexity_score,
                "max_complexity": max_complexity,
                "patterns": zxcvbn_result,
                "crack_times": zxcvbn_result.get("crack_times_display", {}),
                "breach_status": is_leaked,
                "breach_message": breach_message,
                "strength": strength_rating,
            }
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Analysis failed: {e}[/red]")
            return False


def main():
    """Main CLI entry point."""
    console = Console()
    
    # Header
    console.print(
        Panel(
            "[bold cyan]🔐 Password Strength Checker[/bold cyan]\n"
            "[dim]Comprehensive security analysis with breach detection[/dim]",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    
    checker = PasswordStrengthChecker()
    
    while True:
        try:
            # Get and analyze password
            if not checker.analyze():
                console.print("[yellow]Analysis failed. Please try again.[/yellow]")
                continue
            
            # Display results
            checker.display_results()
            
            # Prompt for next action
            choice = input("Check another password? (y/n): ").strip().lower()
            if choice != 'y':
                console.print("[cyan]✓ Thank you for using Password Strength Checker![/cyan]\n")
                break
            
            # Reset for next iteration
            checker = PasswordStrengthChecker()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]\n")
            break
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            break


if __name__ == "__main__":
    main()
