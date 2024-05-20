import sys
import string
import random
import math
import argparse
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog


def main():
    args = parse_args()

    if args is None:
        interactive()
    else:
        automatic(args)


def automatic(args):
    charset = make_charset(args.use_upper, args.use_lower, args.use_digits, args.use_punctuation, args.use_space, args.additional, args.blacklist)

    if not args.quiet:
        print("***** Password Generator *****")
        print()
        print("Using this character set (excluding the arrows): ")
        print("→{}←".format("".join(sorted(charset))))
        print("There may be at most {} occurrences of the same character per password.".format(args.max_duplicate_chars) if args.max_duplicate_chars > 0 else "There are no duplicate character limits.")
        print()
        print("Generating {} password{} of length {}:".format(args.amount, "s" if args.amount > 1 else "", args.length))
        print()

    for _ in range(args.amount):
        password = generate_password(charset, args.length, args.max_duplicate_chars)
        print(password)


def interactive():
    def generate():
        charset = make_charset(upper_var.get(), lower_var.get(), digits_var.get(), punctuation_var.get(), space_var.get(), additional_entry.get(), blacklist_entry.get())
        length = int(length_entry.get())
        max_duplicate_chars = int(max_dupe_entry.get()) if max_dupe_entry.get() else 0
        password = generate_password(charset, length, max_duplicate_chars)
        password_entry.config(state=tk.NORMAL)
        password_entry.delete(0, tk.END)
        password_entry.insert(0, password)
        password_entry.config(state='readonly')

    root = tk.Tk()
    root.title("Password Generator")

    tk.Label(root, text="Length:").grid(row=0, column=0)
    length_entry = tk.Entry(root)
    length_entry.grid(row=0, column=1)
    length_entry.insert(0, "12")

    upper_var = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Include Uppercase", variable=upper_var).grid(row=1, column=0, columnspan=2, sticky='w')

    lower_var = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Include Lowercase", variable=lower_var).grid(row=2, column=0, columnspan=2, sticky='w')

    digits_var = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Include Digits", variable=digits_var).grid(row=3, column=0, columnspan=2, sticky='w')

    punctuation_var = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Include Punctuation", variable=punctuation_var).grid(row=4, column=0, columnspan=2, sticky='w')

    space_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="Include Spaces", variable=space_var).grid(row=5, column=0, columnspan=2, sticky='w')

    tk.Label(root, text="Additional Characters:").grid(row=6, column=0)
    additional_entry = tk.Entry(root)
    additional_entry.grid(row=6, column=1)

    tk.Label(root, text="Blacklist Characters:").grid(row=7, column=0)
    blacklist_entry = tk.Entry(root)
    blacklist_entry.grid(row=7, column=1)

    tk.Label(root, text="Max Duplicate Characters (0 for no limit):").grid(row=8, column=0)
    max_dupe_entry = tk.Entry(root)
    max_dupe_entry.grid(row=8, column=1)

    tk.Button(root, text="Generate Password", command=generate).grid(row=9, column=0, columnspan=2)

    password_entry = tk.Entry(root, state='readonly', width=50)
    password_entry.grid(row=10, column=0, columnspan=2)

    root.mainloop()


def parse_args():
    if len(sys.argv) <= 1:
        # no arguments --> interactive mode
        return None

    parser = argparse.ArgumentParser(description="Highly customizable random password generator",
                                     epilog="Run it without any arguments for interactive mode.")

    parser.add_argument("length", action="store", type=int,
                        help="length of the password to generate")
    parser.add_argument("-n", "--amount", action="store", type=int, dest="amount", default=1,
                        help="how many passwords to create")
    parser.add_argument("-m", "--max-duplicate-chars", action="store", dest="max_duplicate_chars", type=int, default=0, metavar="LIMIT",
                        help="limits how often the same character may occur in a password at most")

    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                        help="print only one password per line, nothing else")

    p_charset = parser.add_argument_group("Character set specification")
    p_charset.add_argument("-u", "--uppercase", action="store_true", dest="use_upper",
                           help="include uppercase letters A-Z into the available character set")
    p_charset.add_argument("-l", "--lowercase", action="store_true", dest="use_lower",
                           help="include lowercase letters a-z into the available character set")
    p_charset.add_argument("-d", "--digits", action="store_true", dest="use_digits",
                           help="include digits 0-9 into the available character set")
    p_charset.add_argument("-p", "--punctuation", action="store_true", dest="use_punctuation",
                           help="include punctuation into the available character set")
    p_charset.add_argument("-s", "--space", action="store_true", dest="use_space",
                           help="include the standard space into the available character set")

    p_charset.add_argument("-a", "--additional", action="store", default="", dest="additional",
                           help="additional characters to include into the available character set")
    p_charset.add_argument("-b", "--blacklist", action="store", default="", dest="blacklist",
                           help="characters to exclude from the available character set")

    args = parser.parse_args()
    if not any([args.use_upper, args.use_lower, args.use_digits, args.use_punctuation, args.use_space,
               args.additional]):
        parser.error("You must enable at least one character class or add custom characters!")
    return args


def ask_yn(message, default):
    if not isinstance(message, str) or not isinstance(default, bool):
        raise TypeError

    msg = message + (" (Y/n) " if default else " (y/N) ")
    while True:
        answer = input(msg).lower().strip()
        if not answer:
            return default
        if answer in "yn":
            return answer == "y"
        print("Sorry, please do only enter [y] or [n] or leave it blank to accept the default. Try again!")


def make_charset(use_upper, use_lower, use_digits, use_punctuation, use_space, additional, blacklist):
    if not all(isinstance(x, bool) for x in [use_upper, use_lower, use_digits, use_punctuation, use_space]) \
            or not all(isinstance(x, str) for x in [additional, blacklist]):
        raise TypeError

    return set(use_upper * string.ascii_uppercase +
               use_lower * string.ascii_lowercase +
               use_digits * string.digits +
               use_punctuation * string.punctuation +
               use_space * " " +
               additional) \
        .difference(set(blacklist))


def generate_password(charset, length, max_duplicate_chars):
    if not isinstance(charset, set) or not isinstance(length, int) or not isinstance(max_duplicate_chars, int):
        raise TypeError
    my_charset = charset.copy()
    password = ""
    while len(password) < length:
        password += random.SystemRandom().choice(list(my_charset))
        if max_duplicate_chars:
            for c in set(password):
                if password.count(c) >= max_duplicate_chars:
                    my_charset.discard(c)
    return password


if __name__ == "__main__":
    main()
