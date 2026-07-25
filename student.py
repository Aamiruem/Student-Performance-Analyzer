class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def total(self):
        return sum(self.marks)

    def average(self):
        return self.total() / len(self.marks)

    def is_pass(self, pass_mark=35):
        return all(m >= pass_mark for m in self.marks)
