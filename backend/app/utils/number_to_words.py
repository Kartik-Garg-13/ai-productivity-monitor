_ONES = [
    "",
    "One",
    "Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine",
    "Ten",
    "Eleven",
    "Twelve",
    "Thirteen",
    "Fourteen",
    "Fifteen",
    "Sixteen",
    "Seventeen",
    "Eighteen",
    "Nineteen",
]
_TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def _two_digits(n: int) -> str:
    if n < 20:
        return _ONES[n]
    return f"{_TENS[n // 10]} {_ONES[n % 10]}".strip()


def _three_digits(n: int) -> str:
    if n >= 100:
        return f"{_ONES[n // 100]} Hundred {_two_digits(n % 100)}".strip()
    return _two_digits(n)


def amount_in_words_rupees(amount) -> str:
    """Convert numeric amount to Indian Rupee words."""
    from decimal import Decimal, ROUND_HALF_UP

    value = Decimal(str(amount)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    n = int(value)
    if n == 0:
        return "Zero Rupees Only"

    parts = []
    crore = n // 10000000
    n %= 10000000
    lakh = n // 100000
    n %= 100000
    thousand = n // 1000
    n %= 1000
    hundred_rest = n

    if crore:
        parts.append(f"{_two_digits(crore)} Crore")
    if lakh:
        parts.append(f"{_two_digits(lakh)} Lakh")
    if thousand:
        parts.append(f"{_two_digits(thousand)} Thousand")
    if hundred_rest:
        parts.append(_three_digits(hundred_rest))

    return " ".join(parts) + " Rupees Only"
