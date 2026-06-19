class Customer:
    def __init__(self, name,phone,email,address=""):
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address

    def to_dict(self):
        """Convert Customer data to a dictionary for JSON serialization"""
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address
        }

    @staticmethod
    def from_dict(data):
        """Create Customer object  from a dictionary for JSON serialization"""
        return Customer(data["name"],data["phone"],data["email"],data["address"])