# Characters that take more than one code point in unicode. These need to be
# manually added to the character ROM.
super_minus: str = "\u207b"
super_one: str = "\u00B9"
inverse: str = f"{super_minus}{super_one}"
x_bar: str = "x̄"

# Characters which only require one code point, but are difficult to type
# and/or are ambiguous.
hbar = "―"  # Intended to be a katakana character?
block = "█"

# Japanese punctuation. The CFA533, at least, contains Katakana characters
# with corresponding punctuation in its character ROM.
japan_interpunct = "・"
japan_lquote = "「"
japan_rquote = "」"
japan_full_stop = "。"
japan_comma = "、"
