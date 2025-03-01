from __init__ import CURSOR, CONN
from department import Department

class Employee:
    all = {}
    
    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id
        
    @property
    def name(self):
        return self._name
        
    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        if not value:
            raise ValueError("Name must not be empty")
        self._name = value
        
    @property
    def job_title(self):
        return self._job_title
        
    @job_title.setter
    def job_title(self, value):
        if not isinstance(value, str):
            raise ValueError("Job title must be a string")
        if not value:
            raise ValueError("Job title must not be empty")
        self._job_title = value
        
    @property
    def department_id(self):
        return self._department_id
        
    @department_id.setter
    def department_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Department ID must be an integer")
            
        # Check if department exists
        sql = "SELECT * FROM departments WHERE id = ?"
        CURSOR.execute(sql, (value,))
        result = CURSOR.fetchone()
        
        if not result:
            raise ValueError(f"No department exists with id {value}")
            
        self._department_id = value
    
    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Department: {self.department_id}>"
    
    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id))
        """
        CURSOR.execute(sql)
        CONN.commit()
    
    @classmethod
    def drop_table(cls):
        sql = """
            DROP TABLE IF EXISTS employees;
        """
        CURSOR.execute(sql)
        CONN.commit()
    
    def save(self):
        if self.id is None:
            sql = """
                INSERT INTO employees (name, job_title, department_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Employee.all[self.id] = self
        return self
    
    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        return employee.save()
    
    @classmethod
    def instance_from_db(cls, row):
        employee_id = row[0]
        if employee_id in cls.all:
            employee = cls.all[employee_id]
            # Update attributes to match the row
            employee._name = row[1]
            employee._job_title = row[2]
            employee._department_id = row[3]
            return employee
        employee = cls(row[1], row[2], row[3], row[0])
        cls.all[employee_id] = employee
        return employee
    
    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM employees WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None
    
    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM employees WHERE name = ?"
        CURSOR.execute(sql, (name,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None
    
    def update(self):
        sql = """
            UPDATE employees
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()
    
    def delete(self):
        sql = "DELETE FROM employees WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        
        if self.id in Employee.all:
            del Employee.all[self.id]
            
        self.id = None
    
    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM employees"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
    
    def department(self):
        return Department.find_by_id(self.department_id)
    
    def reviews(self):
        """Return a list of Review instances associated with this employee"""
        # Import Review inside the method to avoid circular imports
        from review import Review
        
        sql = "SELECT * FROM reviews WHERE employee_id = ?"
        CURSOR.execute(sql, (self.id,))
        rows = CURSOR.fetchall()
        
        return [Review.instance_from_db(row) for row in rows]