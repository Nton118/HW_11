from collections import UserDict
from datetime import datetime
from functools import wraps
from itertools import islice
import re

PAGE = 10


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value


class Name(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if not (value.isnumeric() or len(value) < 3):  # Name validation
            self.__value = value
        else:
            raise ValueError


class Birthday(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        try:
            self.__value = datetime.strptime(value, "%d.%m.%Y")  # Date validaiton "."
        except ValueError:
            self.__value = datetime.strptime(value, "%d/%m/%Y")  # Date validaiton "/"

    def __str__(self) -> str:
        return datetime.strftime(self.value, "%d.%m.%Y")


class Email(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        pattern = (
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"  # Email validation
        )
        if re.match(pattern, value):
            self.__value = value
        else:
            raise ValueError


class Phone(Field):
    min_len = 5
    max_len = 17

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        new_phone = (  # Phone validation
            value.strip()
            .removeprefix("+")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
        )
        if (
            not new_phone.isdecimal()
            or not Phone.min_len <= len(new_phone) <= Phone.max_len
        ):
            raise TypeError
        self.__value = new_phone


class Record:
    def __init__(
        self,
        name: Name,
        phone: Phone = None,
        birthday: Birthday = None,
        email: Email = None,
    ):
        self.name = name
        self.phones = []
        if phone:
            self.phones.append(phone)
        self.birthday = birthday
        self.email = email

    def __str__(self):
        return f"{self.name}: Phones: {', '.join([str(phone) for phone in self.phones])}; E-mail:{self.email}; B-day:{self.birthday} \n"

    def __repr__(self):
        return f"{self.name}: Phones: {', '.join([str(phone) for phone in self.phones])}; E-mail:{self.email}; B-day:{self.birthday} \n"

    def days_to_birthday(self) -> int:
        today = datetime.today()
        compare = self.birthday.value.replace(year=today.year)
        if int((compare - today).days) > 0:
            return f"{int((compare - today).days)} days to birthday"
        elif today.month == compare.month and today.day == compare.day:
            return "It is TODAY!!!"
        else:
            return f"{int((compare.replace(year=today.year+1) - today).days)} days to birthday"

    def add_phone(self, phone: Phone):
        self.phones.append(phone)

    def add_email(self, email: Email):
        self.email = email

    def add_birthday(self, birthday: Birthday):
        if not self.birthday:
            self.birthday = birthday
        else:
            raise IndexError("Birthday already entered")

    def show_phones(self):
        if not self.phones:
            return "this contact has no phones."
        elif len(self.phones) == 1:
            return f"Current phone number is {self.phones[0]}"
        else:
            output = "This contact has several phones:\n"
            for i, phone in enumerate(self.phones, 1):
                output += f"{i}: {phone} "
            return output

    def del_phone(self, num=1):
        if not self.phones:
            raise IndexError
        else:
            return self.phones.pop(num - 1)

    def edit_phone(self, phone_new: Phone, num=1):
        if not self.phones:
            raise IndexError
        else:
            self.phones.pop(num - 1)
            self.phones.insert(num - 1, phone_new)


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data.update({record.name.value: record})

    def remove_record(self, contact: str):
        return self.data.pop(contact)

    def show_phone(self, contact: str):
        return self.data.get(contact).show_phones()

    def iterator(self, page):
        start = 0
        while True:
            output = ""
            for i in islice(self.data.values(), start, start + page):
                output += str(i)
            if not output:
                output = f"Total: {len(self.data)} contacts."
                yield output
                break
            yield output
            start += page

    def show_all(self):
        output = ""
        for contact in self.data.values():
            output += str(contact)
        output += f"Total: {len(self.data)} contacts."
        return output


is_ended = False

book1 = AddressBook()


def input_error(func):
    @wraps(func)
    def wrapper(*args):
        try:
            result = func(*args)
            return result

        except TypeError:
            if func.__name__ == "handler":
                return "No such command!"
            if func.__name__ == "add" or func.__name__ == "change":
                return f"Give me name and phone please. Minimum phone number length is {Phone.min_len} digits. Maximum {Phone.max_len}.Letters not allowed!"
            if func.__name__ == "add_birthday":
                return "input name and date"
            if func.__name__ == "add_email":
                return "input name and e-mail"

        except AttributeError:
            return 'No such contact! to add one use "add" command'

        except ValueError:
            if func.__name__ == "add" or func.__name__ == "change":
                return "Name cannot consist of only digits and min name length is 3."
            if func.__name__ == "phone":
                return "Enter contact name"
            if func.__name__ == "show_all":
                return "The Phonebook is empty"
            if func.__name__ == "del_phone":
                return "this contact doesn't have such phone number"
            if func.__name__ == "add_birthday":
                return "use date format DD.MM.YYYY or DD/MM/YYYY"
            if func.__name__ == "add_email":
                return "invalid email format"

        except IndexError:
            if func.__name__ == "add_birthday":
                return "Birth date lready entered, only one allowed"
            else:
                return "Command needs no arguments"

    return wrapper


@input_error
def greet(*args):
    if args != ("",):
        raise IndexError
    return "How can I help you?"


@input_error
def add(contact: str, phone: str = None):
    contact_new = Name(contact)
    phone_new = Phone(phone) if phone else None
    rec_new = Record(contact_new, phone_new)

    if contact not in book1.keys():
        book1.add_record(rec_new)
        return f'Added contact "{contact}" with phone number: {phone}'
    else:
        book1.get(contact).add_phone(phone_new)
        return f'Updated existing contact "{contact}" with new phone number: {phone}'


@input_error
def add_email(contact: str, email: str):
    email_new = Email(email)
    rec = book1.get(contact)
    rec.add_email(email_new)
    return f'Updated existing contact "{contact}" with new email: {email}'


@input_error
def add_birthday(contact: str, birthday: str):
    b_day = Birthday(birthday)
    rec = book1.get(contact)
    rec.add_birthday(b_day)
    return f'Updated existing contact "{contact}" with a birth date: {b_day}'


@input_error
def congrat(contact: str):
    rec = book1.get(contact)

    return rec.days_to_birthday()


@input_error
def change(contact: str, phone: str = None):
    rec = book1.get(contact)

    print(book1.show_phone(contact))

    if not rec.phones:
        if not phone:
            phone_new = Phone(input("If you want to add the phone enter phone number:"))
        else:
            phone_new = Phone(phone)
        rec.add_phone(phone_new)
        return f'Changed phone number to {phone_new} for contact "{contact}"'

    else:
        if len(rec.phones) == 1:
            num = 1
        if len(rec.phones) > 1:
            num = int(input("which one do yo want to change (enter index):"))
        if not phone:
            phone_new = Phone(input("Please enter new phone number:"))
        else:
            phone_new = Phone(phone)
        old_phone = rec.phones[num - 1]
        rec.edit_phone(phone_new, num)
        return (
            f'Changed phone number {old_phone} to {phone_new} for contact "{contact}"'
        )


@input_error
def del_phone(contact: str, phone=None):
    rec = book1.get(contact)

    if phone:
        for i, p in enumerate(rec.phones):
            if p == phone:
                num = i + 1
        else:
            raise ValueError
    else:
        print(rec.show_phones())
        if len(rec.phones) == 1:
            num = 1
            ans = None
            while ans != "y":
                ans = input(
                    f"Contact {rec.name} has only 1 phone {rec.phones[0]}. Are you sure? (Y/N)"
                ).lower()
        else:
            num = int(input("which one do yo want to delete (enter index):"))
    return f"Phone {rec.del_phone(num)} deleted!"


@input_error
def del_email(contact: str, email=None):
    rec = book1.get(contact)
    rec.email = None
    return f"Contact {contact}, email deleted"


@input_error
def del_contact(contact: str):
    rec = book1.get(contact)
    if not rec:
        raise AttributeError
    ans = None
    while ans != "y":
        ans = input(f"Are you sure to delete contact {contact}? (Y/N)").lower()
    return f"Contact {book1.remove_record(contact)} deleted!"


@input_error
def del_birthday(contact: str):
    rec = book1.get(contact)
    rec.birthday = None
    return f"Contact {contact}, birthday deleted"


@input_error
def phone(contact: str):
    return f'Contact "{contact}". {book1.show_phone(contact)}'


@input_error
def show_all(*args):
    if args != ("",):
        raise IndexError
    if len(book1) < PAGE:
        return book1.show_all()
    else:
        gen_obj = book1.iterator(PAGE)
        for i in gen_obj:
            print(i)
            print("*" * 50)
            input("Press any key")


@input_error
def help(*args):
    if args != ("",):
        raise IndexError
    return f"available commands: {', '.join(k for k in COMMANDS.keys())}"


@input_error
def exit(*args):
    if args != ("",):
        raise IndexError
    global is_ended
    is_ended = True
    return "Good bye!"


COMMANDS = {
    "hello": greet,
    "add email": add_email,
    "add b_day": add_birthday,
    "add": add,
    "congrat": congrat,
    "change": change,
    "phone": phone,
    "show all": show_all,
    "del phone": del_phone,
    "del b_day": del_birthday,
    "del email": del_email,
    "del contact": del_contact,
    "close": exit,
    "good bye": exit,
    "exit": exit,
    "help": help,
}


def command_parser(line: str):
    line_prep = " ".join(line.split())
    for k, v in COMMANDS.items():
        if line_prep.lower().startswith(k + " ") or line_prep.lower() == k:
            return v, re.sub(k, "", line_prep, flags=re.IGNORECASE).strip().rsplit(
                " ", 1
            )
    return None, []


@input_error
def handler(command, args):
    return command(*args)


def main():
    while not is_ended:
        s = input(">>>")

        command, args = command_parser(s)
        print(handler(command, args))


if __name__ == "__main__":
    main()
