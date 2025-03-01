from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:
    # Dictionary of objects saved to the database.
    all = {}
    
    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id
    
    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )
    
    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INT,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()
    
    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()
    
    @property
    def year(self):
        return self._year
    
    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer")
        if value < 2000:
            raise ValueError("Year must be greater than or equal to 2000")
        self._year = value
    
    @property
    def summary(self):
        return self._summary
    
    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Summary must be a non-empty string")
        self._summary = value
    
    @property
    def employee_id(self):
        return self._employee_id
    
    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Employee ID must be an integer")
        
        # Check if the employee exists in the database
        sql = "SELECT * FROM employees WHERE id = ?"
        CURSOR.execute(sql, (value,))
        result = CURSOR.fetchone()
        
        if not result:
            raise ValueError(f"No employee exists with id {value}")
        
        self._employee_id = value
    
    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
            Update object id attribute using the primary key value of new row.
            Save the object in local dictionary using table row's PK as dictionary key"""
        
        if self.id is None:
            # Insert a new row
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            
            # Update the object's ID
            self.id = CURSOR.lastrowid
            
            # Save the object in the dictionary
            Review.all[self.id] = self
        
        return self
    
    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        return review.save()
    
    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        # Check the dictionary for existing instance using the row's primary key
        review_id = row[0]
        
        # If the dictionary already has this review, update it with new values and return it
        if review_id in cls.all:
            review = cls.all[review_id]
            # Update attributes to match the row
            review._year = row[1]
            review._summary = row[2]
            review._employee_id = row[3]
            return review
        
        # Otherwise, create a new Review instance and add it to the dictionary
        review = cls(row[1], row[2], row[3], row[0])
        cls.all[review_id] = review
        return review
    
    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        
        if row:
            return cls.instance_from_db(row)
        return None
    
    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()
        return self
    
    def delete(self):
        """Delete the table row corresponding to the current Review instance,
            delete the dictionary entry, and reassign id attribute"""
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        
        # Remove from dictionary if present
        if self.id in Review.all:
            del Review.all[self.id]
        
        # Reset ID to None
        self.id = None
        return self
    
    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        
        return [cls.instance_from_db(row) for row in rows]