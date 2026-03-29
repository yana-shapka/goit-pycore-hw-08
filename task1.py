from collections import UserDict
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Callable


class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    def __init__(self, value: str):
        if not value or not value.strip():
            raise ValueError("Name is required.")
        super().__init__(value.strip())


class Phone(Field):
    def __init__(self, value: str):
        if not self._validate(value):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

    def _validate(self, value: str) -> bool:
        return value.isdigit() and len(value) == 10


class Birthday(Field):
    def __init__(self, value: str):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self) -> str:
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def find_phone(self, phone: str) -> Optional[Phone]:
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def remove_phone(self, phone: str):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)

    def edit_phone(self, old_phone: str, new_phone: str):
        phone_obj = self.find_phone(old_phone)
        if phone_obj is None:
            raise ValueError(f"Phone {old_phone} not found.")
        index = self.phones.index(phone_obj)
        self.phones[index] = Phone(new_phone)

    def add_birthday(self, date_str: str):
        self.birthday = Birthday(date_str)

    def __str__(self) -> str:
        phones = "; ".join(p.value for p in self.phones)
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        return self.data.get(name)

    def delete(self, name: str):
        self.data.pop(name, None)

    def get_upcoming_birthdays(self) -> List[dict]:
        upcoming = []
        today = datetime.today().date()

        for record in self.data.values():
            if not record.birthday:
                continue

            try:
                bday = record.birthday.value.replace(year=today.year)
            except ValueError:
                bday = record.birthday.value.replace(year=today.year, month=3, day=1)

            if bday < today:
                try:
                    bday = bday.replace(year=today.year + 1)
                except ValueError:
                    bday = bday.replace(year=today.year + 1, month=3, day=1)

            if 0 <= (bday - today).days <= 7:
                if bday.weekday() >= 5:
                    bday += timedelta(days=7 - bday.weekday())
                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": bday.strftime("%d.%m.%Y")
                })

        return upcoming


def input_error(func: Callable) -> Callable:
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            msg = str(e)
            if "not enough values to unpack" in msg:
                return "Give me name and phone please."
            return msg
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter the argument for the command."
    return inner


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    if not user_input.strip():
        return "", []
    cmd, *args = user_input.split()
    return cmd.strip().lower(), args


@input_error
def add_contact(args: List[str], book: AddressBook) -> str:
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        record.add_phone(phone)
        return "Contact added."
    record.add_phone(phone)
    return "Phone added to existing contact."


@input_error
def change_contact(args: List[str], book: AddressBook) -> str:
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args: List[str], book: AddressBook) -> str:
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    return str(record)


@input_error
def add_birthday(args: List[str], book: AddressBook) -> str:
    name, date = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.add_birthday(date)
    return "Birthday added."


@input_error
def show_birthday(args: List[str], book: AddressBook) -> str:
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    if record.birthday is None:
        return "Birthday not set."
    return f"{name}'s birthday: {record.birthday}"


@input_error
def birthdays(args: List[str], book: AddressBook) -> str:
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next 7 days."
    return "Upcoming birthdays:\n" + "\n".join(
        f"{b['name']}: {b['congratulation_date']}" for b in upcoming
    )


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if not command:
            continue

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            if not book.data:
                print("Address book is empty.")
            else:
                for record in book.data.values():
                    print(record)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()