from dataclasses import dataclass


def congregate_zeroes(number: int | float, keep_zeroes_threshold=3):
    """Converts a number to scientific notation but uses whole numbers
    as factor and only congregates consecutive trailing zeroes into the exponent.

    Will only use scientific notation if there are more than `keep_zeroes_threshold` trailing zeroes.
    """

    trailing_zeroes = 0
    cropped_number = number
    while (cropped_number % 10 == 0 and cropped_number != 0):
        cropped_number = cropped_number // 10
        trailing_zeroes += 1
    if trailing_zeroes > keep_zeroes_threshold:

        if isinstance(cropped_number, int) or cropped_number.is_integer():
            factor = str(int(cropped_number))
        else:
            factor = str(cropped_number)
        exponent = "{:+}".format(trailing_zeroes)
        f_number = factor + "e" + exponent

    else:
        f_number = str(number)

    return f_number


def number_to_scientific(number: int | float, max_keep=1_000, min_keep=0.1, max_digits=8):
    """Formats the number according to its size and length.
    Numbers that are either
        - greater or equal to `max_keep` (default: 10,000)
        - less than `min_keep` (default: 0.1)
    will be converted to scientific notation.

    Numbers, which do not get scientific notation
    but are too long (more than `max_digits` (default: 9) digits) will get cropped and get an ellipsis
     added as indicator for the cropping.

    This is intended to shorten numbers to make them viewable in small text entries while keeping a more natural,
    non-scientific look for already short numbers.
    """
    if number >= max_keep or number < min_keep:
        # If the number is between these ranges, use scientific notation.
        f_number = "{:.4e}".format(number)
    else:
        # If the number is between the number ranges above,
        # do not use scientific notation but crop it if it is too long.
        # It can be too long and between those ranges if it is small but has a lot of decimal places.
        f_number = str(number)
        if len(f_number) > max_digits:
            f_number = f_number[:max_digits - 2] + "..."
            # ↑ Crop down two more characters than the limit to account for the added space from the dots.
    return f_number


if __name__ == '__main__':
    print(congregate_zeroes(1_200_000))
    print(congregate_zeroes(13_001_000_000))
    print(congregate_zeroes(13.001_000_000))
    print(congregate_zeroes(1.0))
    print(congregate_zeroes(100000.0))
    print(congregate_zeroes(1000))
