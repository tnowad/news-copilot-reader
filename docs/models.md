# Models

1. **User**:

   - Fields: username, email, password (hashed), role
   - Relationships:
     - Many-to-many relationship with Roles
     - One-to-many relationship with Comments
     - Many-to-many relationship with Articles (as Reader)
     - Many-to-many relationship with Articles (as Bookmark)

2. **Role**:

   - Fields: name
   - Relationships:
     - Many-to-many relationship with Users
     - Many-to-many relationship with Permissions

3. **Article**:

   - Fields: title, content, category, tags, date_created
   - Relationships:
     - Many-to-one relationship with Users (as Writer)
     - Many-to-many relationship with Users (as Reader)
     - Many-to-many relationship with Categories
     - One-to-many relationship with Comments

4. **Category**:

   - Fields: name
   - Relationships:
     - Many-to-many relationship with Articles

5. **Comment**:

   - Fields: content, date_created
   - Relationships:
     - Many-to-one relationship with Users
     - Many-to-one relationship with Articles

6. **Permission**:

   - Fields: name
   - Relationships:
     - Many-to-many relationship with Roles

7. **Bookmark**:
   - Fields: user_id, article_id
   - Relationships:
     - Many-to-one relationship with Users
     - Many-to-one relationship with Articles
