# Client Dashboard - Admin Panel

A modern web-based dashboard for managing and visualizing client data across different categories. Built with Flask, MySQL, and Chart.js.

## Features

- **Admin Authentication**: Secure login system
- **Interactive Charts**: Pie chart, bar chart, and line chart visualizations
- **Real-time Statistics**: Live data from MySQL database
- **Responsive Design**: Works on desktop and mobile devices
- **100 Sample Clients**: Pre-populated with 10 different categories
- **Complete Client Management**: Add, edit, delete, and view client details
- **Advanced Search & Filtering**: Search by name and filter by category
- **Bulk Operations**: Bulk delete and category updates
- **Import/Export Functionality**: CSV and JSON export options
- **Database Management**: Backup, restore, and optimization tools
- **Comprehensive Logging**: System logs and activity tracking

## Prerequisites

- Python 3.7+
- MySQL Server (XAMPP recommended for easy setup)
- pip (Python package manager)

## Installation

### 1. Clone or Download the Project

Navigate to the `usird` directory containing the project files.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up MySQL Database

#### Option A: Using XAMPP (Recommended for easy setup)

1. **Install and Start XAMPP**
   - Download from: https://www.apachefriends.org/
   - Install XAMPP
   - Start XAMPP Control Panel
   - Start MySQL service from the control panel
   - Or use command line: `sudo /opt/lampp/lampp start`

2. **Run Automated Setup Script**
   ```bash
   # This will automatically set up the database and import sample data
   ./setup.sh
   ```

   The setup script will:
   - Check XAMPP MySQL status
   - Create the database and tables
   - Import 100 sample clients
   - Handle MySQL version compatibility issues

#### Option B: Manual Database Setup

1. **Start MySQL Server**
   ```bash
   sudo systemctl start mysql
   # or
   sudo service mysql start
   ```

2. **Create MySQL User** (if not exists)
   ```sql
   CREATE USER 'usird'@'localhost' IDENTIFIED BY 'usrid';
   GRANT ALL PRIVILEGES ON client_data.* TO 'usird'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Import Database Schema and Data**
   ```bash
   mysql -u root -p < client_data_create.sql
   ```

### 4. Configure Database Connection

The application automatically detects and uses XAMPP MySQL. For custom configurations, edit `server.py` and update the MySQL connection details if needed:

```python
db = mysql.connector.connect(
    host="localhost",
    user="root",  # XAMPP default
    password="",  # XAMPP default (no password)
    database="client_data"
)
```

## Running the Application

### 1. Start the Flask Server

```bash
python3 server.py
```

### 2. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

### 3. Login Credentials

The system now uses database-based authentication with multiple user accounts:

#### Default Users (created automatically):
- **Admin User**:
  - Username: `admin`
  - Password: `admin123`
  - Role: Administrator
  - Email: admin@example.com

- **Manager User**:
  - Username: `manager`
  - Password: `admin`
  - Role: Manager
  - Email: manager@example.com

- **Regular User**:
  - Username: `user`
  - Password: `user`
  - Role: User
  - Email: user@example.com

#### User Roles:
- **Admin**: Full access to all features including user management
- **Manager**: Access to client management and reports
- **User**: Basic access to view data and export

## Project Structure

```
usird/
├── server.py                    # Flask application server
├── templates/                   # HTML templates directory
│   ├── login.html              # Admin login page
│   ├── dashboard.html          # Main dashboard interface
│   ├── clients.html            # Client management page
│   ├── categories.html         # Category management page
│   ├── analytics.html          # Analytics and reports
│   ├── settings.html           # System settings
│   ├── database.html           # Database management
│   ├── logs.html               # System logs
│   ├── reports.html            # Report generation
│   ├── export.html             # Data export tools
│   ├── profile.html            # User profile management
│   ├── recent.html             # Recent activity
│   ├── overview.html           # System overview
│   ├── 404.html                # Error page
│   └── 500.html                # Server error page
├── client_data_create.sql      # Database schema and sample data
├── update_database.sql         # Database migration script
├── add_timestamps.sql          # Timestamp columns migration
├── requirements.txt            # Python dependencies
├── setup.sh                    # Automated setup script
└── README.md                   # This file
```

## Database Schema

The application uses two main tables:

### Clients Table
Enhanced `clients` table with comprehensive client information:

```sql
CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Users Table
User authentication and management table:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(100),
    role ENUM('admin', 'user', 'manager') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);
```

### Sample Categories

The database comes pre-populated with 100 clients across 10 categories:

1. **Technology** (10 clients)
2. **Healthcare** (10 clients)
3. **Finance** (10 clients)
4. **Education** (10 clients)
5. **Immigration** (10 clients)
6. **Manufacturing** (10 clients)
7. **Real Estate** (10 clients)
8. **Transportation** (10 clients)
9. **Marketing** (10 clients)
10. **Consulting** (10 clients)

## Dashboard Features

### Client Management

- **Add New Clients**: Complete form with name, category, email, phone, address, and notes
- **Edit Clients**: Full editing capabilities with all fields populated
- **Delete Clients**: Individual and bulk deletion options
- **View Client Details**: Comprehensive client information display
- **Search & Filter**: Search by name and filter by category
- **Pagination**: Efficient handling of large client lists

### Charts and Visualizations

1. **Client Distribution Pie Chart**: Shows the distribution of clients across categories
2. **Category Breakdown Bar Chart**: Displays the number of clients per category
3. **Client Activity Line Chart**: Simulated activity data over time

### Statistics Panel

- Total number of clients
- Number of categories
- Average clients per category
- Largest category size
- Recent client additions

### System Management

- **Database Operations**: Backup, restore, optimize, and test connections
- **Export Tools**: CSV and JSON export with custom formatting
- **Log Management**: View and clear system logs
- **Settings Management**: System configuration options
- **Profile Management**: User profile and password changes
- **User Management**: Add, edit, delete users with role-based access control

## Recent Updates and Fixes

### Database Schema Enhancement
- ✅ Added missing columns: `email`, `phone`, `address`, `notes`
- ✅ Added timestamp tracking: `created_at`, `updated_at`
- ✅ Fixed MySQL version compatibility issues
- ✅ Automated database migration scripts

### Client Management Improvements
- ✅ Fixed add client functionality with complete form support
- ✅ Enhanced edit client with full field population
- ✅ Improved client details view
- ✅ Added bulk operations support
- ✅ Enhanced search and filtering capabilities

### System Stability
- ✅ Fixed MySQL connection issues
- ✅ Improved error handling and logging
- ✅ Enhanced database connection management
- ✅ Added automated setup script

### Authentication & User Management
- ✅ Implemented database-based user authentication
- ✅ Added user management system with role-based access control
- ✅ Created users table with proper password hashing
- ✅ Added user roles (admin, manager, user) with different permissions
- ✅ Enhanced password change functionality with current password verification
- ✅ Added user activity tracking (last login timestamps)

## Security Notes

⚠️ **Important**: This is a demo application with basic security. For production use:

1. Change the secret key in `server.py`
2. Implement proper password hashing
3. Use environment variables for database credentials
4. Enable HTTPS
5. Implement proper session management
6. Add input validation and sanitization
7. Set up proper database user permissions

## Troubleshooting

### Common Issues

1. **MySQL Connection Error**
   - Ensure MySQL server is running
   - For XAMPP: `sudo /opt/lampp/lampp start`
   - Verify database credentials in `server.py`
   - Check if the `client_data` database exists

2. **Database Schema Issues**
   - Run the setup script: `./setup.sh`
   - Or manually run migrations:
     ```bash
     /opt/lampp/bin/mysql -u root < update_database.sql
     /opt/lampp/bin/mysql -u root < add_timestamps.sql
     ```

3. **MySQL Version Compatibility**
   - If you see "Column count of mysql.proc is wrong" error:
     ```bash
     sudo /opt/lampp/bin/mysql_upgrade -u root
     ```

4. **Port Already in Use**
   - Change the port in `server.py` (line 907)
   - Or kill the process using the port

5. **Module Not Found Errors**
   - Run `pip install -r requirements.txt`
   - Ensure you're using Python 3.7+

### Database Reset

To reset the database with fresh sample data:

```bash
# Stop the application first
pkill -f "python.*server.py"

# Drop and recreate database
/opt/lampp/bin/mysql -u root -e "DROP DATABASE IF EXISTS client_data;"
/opt/lampp/bin/mysql -u root < client_data_create.sql

# Restart the application
python3 server.py
```

## Customization

### Adding New Categories

1. Edit `client_data_create.sql`
2. Add new INSERT statements
3. Re-run the SQL file or use the setup script

### Modifying Charts

1. Edit the JavaScript in the respective template files
2. Modify the Chart.js configurations
3. Update the data processing in `server.py`

### Styling Changes

1. Modify the CSS in the template files
2. Update colors, fonts, and layout as needed
3. The application uses modern CSS with responsive design

## API Endpoints

The application provides several REST API endpoints:

- `GET /clients` - List all clients
- `POST /clients/add` - Add new client
- `POST /clients/edit/<id>` - Edit client
- `DELETE /clients/delete/<id>` - Delete client
- `GET /clients/<id>` - Get client details
- `POST /clients/bulk-delete` - Bulk delete clients
- `POST /clients/bulk-update-category` - Bulk update categories
- `GET /export/csv` - Export clients to CSV
- `GET /export/json` - Export clients to JSON

## License

This project is for educational and demonstration purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Flask and MySQL documentation
3. Check the application logs for detailed error messages
4. Ensure all prerequisites are properly installed

## Version History

- **v2.0**: Enhanced database schema, complete client management, bulk operations
- **v1.0**: Basic dashboard with charts and sample data 
