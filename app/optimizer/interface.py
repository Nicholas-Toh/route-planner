from .main import depot, solve, depot
from app.utils.adapters import task_to_customer

class Config:
    mandatory_customers = [] #mandatory tasks
    optional_customers = [] #custom tasks

    def set_mandatory_customers(self, tasks):
        self.mandatory_customers = [task_to_customer(task) for task in tasks]

    def set_optional_customers(self, tasks):
        self.optional_customers = [task_to_customer(task) for task in tasks]
