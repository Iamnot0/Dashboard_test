#!/bin/bash

echo "=== Client Dashboard Setup Script ==="
echo ""


# Check if XAMPP MySQL is running
echo ""
echo "🔍 Checking XAMPP MySQL server status..."

# Check if XAMPP is installed and MySQL is running
if command -v /opt/lampp/bin/mysql &> /dev/null; then
    echo "✅ XAMPP MySQL found"
    if /opt/lampp/bin/mysqladmin ping -h localhost -u root &> /dev/null; then
        echo "✅ XAMPP MySQL server is running"
    else
        echo "⚠️  XAMPP MySQL server is not running. Please start it manually:"
        echo "   sudo /opt/lampp/lampp start"
        echo "   or start XAMPP Control Panel and start MySQL"
    fi
elif command -v /Applications/XAMPP/bin/mysql &> /dev/null; then
    echo "✅ XAMPP MySQL found (macOS)"
    if /Applications/XAMPP/bin/mysqladmin ping -h localhost -u root &> /dev/null; then
        echo "✅ XAMPP MySQL server is running"
    else
        echo "⚠️  XAMPP MySQL server is not running. Please start it manually:"
        echo "   sudo /Applications/XAMPP/xamppfiles/xampp start"
        echo "   or start XAMPP Control Panel and start MySQL"
    fi
else
    echo "⚠️  XAMPP MySQL not found. Please ensure XAMPP is installed and MySQL is running."
    echo "   You can download XAMPP from: https://www.apachefriends.org/"
fi

# Create MySQL user and database
echo ""
echo "🗄️  Setting up MySQL database..."

# Check if XAMPP MySQL is available and use it
if command -v /opt/lampp/bin/mysql &> /dev/null; then
    MYSQL_CMD="/opt/lampp/bin/mysql"
    echo "✅ Using XAMPP MySQL (Linux)"
elif command -v /Applications/XAMPP/bin/mysql &> /dev/null; then
    MYSQL_CMD="/Applications/XAMPP/bin/mysql"
    echo "✅ Using XAMPP MySQL (macOS)"
elif command -v mysql &> /dev/null; then
    MYSQL_CMD="mysql"
    echo "✅ Using system MySQL"
else
    echo "❌ MySQL client not found. Please ensure XAMPP is installed or MySQL is available."
    exit 1
fi

echo "📝 Creating database and importing data..."
echo "Note: If prompted for password, press Enter (XAMPP MySQL root has no password by default)"
$MYSQL_CMD -u root < client_data_create.sql

if [ $? -eq 0 ]; then
    echo "✅ Database setup completed successfully"
else
    echo "❌ Database setup failed. Please check your MySQL credentials and try again."
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To start the application:"
echo "   python3 server.py"
echo ""
echo "Then open your browser and go to:"
echo "   http://localhost:5000"
echo ""
echo "Login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "" 
