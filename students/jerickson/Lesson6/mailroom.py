"""Automate the mailroom workflow.

Run as __main__ to have interface start.
    Can 'mock' the input() function to run through automated 'user' responses
Run as imported module then run main() to start interface.
"""

# pylint: disable=line-too-long

import os


DONATION_DATA_HEADER = ["Name", "Total Given", "# Gifts", "Average Gift"]
donation_data = {
    "Usama Black": {"totalGiven": 22002, "numGifts": 3},
    "Kezia Hassan": {"totalGiven": 3023.23, "numGifts": 3},
    "Lyla Moody": {"totalGiven": 580, "numGifts": 1},
    "King Arthur": {"totalGiven": 400, "numGifts": 1},
    "Twin Arthur": {"totalGiven": 400, "numGifts": 2},
    "Pamela Guerra": {"totalGiven": 32, "numGifts": 2},
    "Malachy Krause": {"totalGiven": 4242, "numGifts": 1},
}


def sort_donation_data():
    """
    Return list of sorted donors by Total-Given

    Returns
    -------
    list
        Sorted donor full-names
    """

    def sort_donor_key(item):
        return item[1]["totalGiven"]

    sorted_donors = [
        name
        for name, _ in sorted(donation_data.items(), key=sort_donor_key, reverse=True)
    ]
    return sorted_donors


def report_cli():
    """Print a report of the donation history."""
    for line in report():
        print(line)


def report():
    """
    Return a list of string-rows of a formatted report of the donation history.

    Donors are sorted in the report in decending order according to total-given amount.
    Produces a 'pretty' ASCII formatted table
    Uses double braces "{{}}" in format strings to dynamically update name field to
    accommodate long donor names without breaking report format.

    Returns
    -------
    list
        ASCII formatted table rows for the report
    """
    report_list = []

    longest_name = len("Name")
    sorted_donor_names = sort_donation_data()

    # Get Longest Donor Name
    for name in sorted_donor_names:
        longest_name = max(longest_name, len(name))

    # Format report lines
    title = DONATION_DATA_HEADER[:]
    name_field_dynamic = "{{:^{:d}}}".format(longest_name + 2)
    report_header = "|{}|  {{:^12}}|{{:^13}}|  {{:^13}}|".format(
        name_field_dynamic
    ).format(*title)
    report_break_list = []
    for char in report_header[:]:
        break_char = "+" if char == "|" else "-"
        report_break_list.append(break_char)
    report_break = "".join(report_break_list)
    report_length = len(report_break)
    report_end = "-" * report_length
    report_title = "|{{:^{:d}}}|".format(report_length - 2).format("Donor Report")

    # Print report Title and Header
    report_list.extend([report_end, report_title, report_break, report_header])

    # Print Sorted Donor Records
    for name in sorted_donor_names:
        total_given = donation_data[name]["totalGiven"]
        num_gifts = donation_data[name]["numGifts"]
        donor_average = float(total_given / num_gifts)
        donor_string = "|{}| ${{:>12.2f}}|{{:^13d}}| ${{:>13.2f}}|".format(
            name_field_dynamic
        ).format(name, total_given, num_gifts, donor_average)

        report_list.extend([report_break, donor_string])

    report_list.append(report_end)
    return report_list


def new_donation(donor_name, amount):
    """
    Add a new donation to the donation record.

    If the donor doesn't exist, they are added.
    The number of gifts and total given update in the donation-data structure.
    The donation amount gets abs() applied to remove negative numbers, no take backs.

    Parameters
    ----------
    donor_name : str
        The string of the donor's full name
    amount : float|int
        The amount of a new donation

    Returns
    -------
    None
    """
    donor_record = donation_data.setdefault(
        donor_name, {"totalGiven": 0, "numGifts": 0}
    )
    donor_record["totalGiven"] += abs(amount)
    donor_record["numGifts"] += 1


def donor_list():
    """
    Return a string of comma seperated donor full-names

    Empty donor-list returns empty string
    Returns
    -------
    str
        Donor names, comma seperated
    """
    return ", ".join(donation_data.keys())


def compose_new_donation_email(donor_name, amount):
    """
    Return a new-donation thank-you email using the donor's historical information.

    Details include the name, new-donation amount, historical number of gifts,
    and the total amount they have donated.

    Parameters
    ----------
    donor_name : str
        The string of the donor's full name
    donor_record : dict
        The summary info of a donor's data
    amount : float|str
        The amount of a new donation, will be called out in the email separately

    Returns
    -------
    email : str
        The composed email
    """
    donor_record = donation_data[donor_name]
    time_s = "times" if donor_record["numGifts"] > 1 else "time"
    email = f"Thank you {donor_name} for your donation of ${amount:.2f}! You have donated {donor_record['numGifts']} {time_s} for a total of ${donor_record['totalGiven']:.2f}."
    return email


def compose_all_donors_emails():
    """
    Creates thank-you emails using each donors' historical information

    Returns
    -------
    dict
        All donor emails in {file_name: contents} pairs
    """
    file_id = 0
    emails = {}
    for donor_name, donor_record in donation_data.items():
        time_s = (
            f"{donor_record['numGifts']:d} donations"
            if donor_record["numGifts"] > 1
            else "donation"
        )  # Grammer correction of donation vs # donations
        email = f"Thank you {donor_name},\n\nYour {time_s} totaling ${donor_record['totalGiven']:.2f} will help us.\n\n{'':>40}Best Regards,\n{'':>40}Jacob Erickson"
        file_name = f"Donor{file_id:03d}_{donor_name}_gitnore.txt"
        file_id += 1

        emails[file_name] = email
    return emails


def save_all_donor_emails():
    """Write to disk thank-you emails for each donor"""
    emails = compose_all_donors_emails()
    for file_name, email in emails.items():
        path = os.path.dirname(os.path.realpath(__file__))

        with open(path + "\\" + file_name, "w") as file:
            file.write(email)


def thank_you_cli():
    """
    Mangages the command-line-interface for the thank_you function inputs

    User input of donor-name and donor-amount, not case-sensitive
        donor-name input: 'list' will show all existing donors
        donor-name input: 'quit' will exit to the main interface and cancel the donation
        donor-amount input: 'quit' will exit to the main interface and cancel the donation
    Print the thank-you email in the terminal
    """
    while True:
        donor_name = input(
            "Who just made a donation? Full Name please, or 'list' to show existing donors. ->: "
        )
        if donor_name.lower() == "list":
            print("All Donors: " + donor_list())
        elif donor_name.lower() == "quit":
            return
        else:
            break  # pragma: no cover (un-testable due to cPython optimization)

    while True:
        try:
            donor_amount = input("How much was the donation? ->: ")
            donor_amount = float(donor_amount)
            break
        except ValueError:
            if donor_amount == "quit":
                return
            print(f"Unrecognized number: {donor_amount}. Try again.")

    print(thank_you(donor_name, donor_amount))


def thank_you(donor_name, donor_amount):
    """
    Add new donation to the record and compose a thank you email to that donor

    Returns
    -------
    email : str
        The thank-you email to the donor, includes historical and recent doncation data.
    """
    new_donation(donor_name, donor_amount)
    email = compose_new_donation_email(donor_name, donor_amount)
    return email


def quit_menu():
    """Return the string "quit" to exit a menu-level"""
    return "quit"


def menu_selection(prompt, dispatch_dict):
    """
    Creates a CLI for users to interact with.

    Manages the flow of the CLI using the parameters. The
    dispatch dictionary controls the function that will be
    called as the result of the user's input. Unrecognized
    commands print an error message to the user and prompts
    them to try again.

    A function that returns 'quit' string will cause the
    loop to break.

    Parameters
    ----------
    prompt : str
        The prompt the user will see in the terminal
    dispatch_dict : dict
        The dictionary where values are callable functions

    Returns
    -------
    None
    """
    while True:
        command = input(prompt).lower()
        try:
            if (
                dispatch_dict[command]() == "quit"
            ):  # Runs command and gets checks if quit is returned
                break
        except KeyError:
            print(f"Unrecognized Command: {command}")


def main():
    """Main function to run user-interace of the mailroom program."""
    command_dispatch = {
        "1": thank_you_cli,
        "2": report_cli,
        "3": save_all_donor_emails,
        "4": quit_menu,
        "quit": quit_menu,
    }
    prompt = "\nChoose: “1”: Send a Thank You, “2”: Create a Report “3”: Send Letters to Everyone or “4”: Quit ->: "
    menu_selection(prompt, command_dispatch)


if __name__ == "__main__":  # pragma: no cover
    main()
