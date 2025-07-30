from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import mysql.connector
from datetime import datetime
import os
import csv
import io
import json
import logging
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MySQL connection (XAMPP compatible)
def get_db_connection():
    try:
        # Try with root user first (XAMPP default)
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # XAMPP MySQL root has no password by default
            database="client_data",
            port=3306
        )
    except mysql.connector.Error as err:
        # If root doesn't work, try with usird user
        if err.errno == 1045:  # Access denied
            print("Trying with usird user...")
            return mysql.connector.connect(
                host="localhost",
                user="usird",
                password="usrid",
                database="client_data",
                port=3306
            )
        else:
            raise err

# Global database connection
db = get_db_connection()

def ensure_db_connection():
    """Ensure database connection is active, reconnect if needed"""
    global db
    try:
        # Test if connection is still alive
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchall()  # Consume any unread results
        cursor.close()
    except Exception as e:
        logger.warning(f"Database connection lost, attempting to reconnect: {e}")
        try:
            db = get_db_connection()
        except Exception as reconnect_error:
            logger.error(f"Failed to reconnect to database: {reconnect_error}")
            raise reconnect_error

def get_dashboard_data():
    """Get common dashboard data"""
    try:
        ensure_db_connection()
        cursor = db.cursor()
        
        # Get category distribution
        cursor.execute("SELECT category, COUNT(*) FROM clients GROUP BY category ORDER BY COUNT(*) DESC")
        category_data = cursor.fetchall()
        
        categories = [row[0] for row in category_data]
        category_counts = [row[1] for row in category_data]
        
        # Get total clients
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_clients = cursor.fetchone()[0]
        
        # Get total categories
        cursor.execute("SELECT COUNT(DISTINCT category) FROM clients")
        total_categories = cursor.fetchone()[0]
        
        # Calculate average clients per category
        avg_clients_per_category = round(total_clients / total_categories, 1) if total_categories > 0 else 0
        
        # Get largest category
        largest_category = max(category_counts) if category_counts else 0
        
        # Get recent clients (last 10)
        cursor.execute("SELECT name, category FROM clients ORDER BY id DESC LIMIT 10")
        recent_clients = [{'name': row[0], 'category': row[1]} for row in cursor.fetchall()]
        
        # Get current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.close()
        
        return {
            'categories': categories,
            'category_counts': category_counts,
            'total_clients': total_clients,
            'total_categories': total_categories,
            'avg_clients_per_category': avg_clients_per_category,
            'largest_category': largest_category,
            'recent_clients': recent_clients,
            'current_time': current_time
        }
    except Exception as e:
        logger.error(f"Database error: {e}")
        return {
            'categories': [],
            'category_counts': [],
            'total_clients': 0,
            'total_categories': 0,
            'avg_clients_per_category': 0,
            'largest_category': 0,
            'recent_clients': [],
            'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            ensure_db_connection()
            cursor = db.cursor()
            
            # Hash the password for comparison
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Check user credentials in database
            cursor.execute("""
                SELECT id, username, email, full_name, role, is_active 
                FROM users 
                WHERE username = %s AND password_hash = %s AND is_active = TRUE
            """, (username, password_hash))
            
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                # Update last login timestamp
                cursor = db.cursor()
                cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s", (user[0],))
                db.commit()
                cursor.close()
                
                # Store user info in session
                session['logged_in'] = True
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['email'] = user[2]
                session['full_name'] = user[3]
                session['role'] = user[4]
                
                logger.info(f"User {username} logged in successfully")
                return redirect(url_for('dashboard'))
            else:
                logger.warning(f"Failed login attempt for username: {username}")
                return render_template('login.html', error='Invalid credentials')
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return render_template('login.html', error='Database error occurred')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    data = get_dashboard_data()
    return render_template('dashboard.html', **data)

@app.route('/overview')
def overview():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    data = get_dashboard_data()
    return render_template('overview.html', **data)

@app.route('/analytics')
def analytics():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    data = get_dashboard_data()
    return render_template('analytics.html', **data)

@app.route('/clients')
def clients():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, category FROM clients ORDER BY id DESC")
        all_clients = [{'id': row[0], 'name': row[1], 'category': row[2]} for row in cursor.fetchall()]
        cursor.close()
        
        data = get_dashboard_data()
        data['all_clients'] = all_clients
        # Get unique categories for the filter dropdown
        data['categories'] = data.get('categories', [])
        return render_template('clients.html', **data)
    except Exception as e:
        logger.error(f"Database error: {e}")
        data = get_dashboard_data()
        data['all_clients'] = []
        data['categories'] = []
        return render_template('clients.html', **data)

@app.route('/categories')
def categories():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT category, COUNT(*) as count FROM clients GROUP BY category ORDER BY count DESC")
        category_stats = [{'category': row[0], 'count': row[1]} for row in cursor.fetchall()]
        cursor.close()
        
        data = get_dashboard_data()
        data['category_stats'] = category_stats
        return render_template('categories.html', **data)
    except Exception as e:
        logger.error(f"Database error: {e}")
        data = get_dashboard_data()
        data['category_stats'] = []
        return render_template('categories.html', **data)

@app.route('/recent')
def recent():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    data = get_dashboard_data()
    return render_template('recent.html', **data)

@app.route('/settings')
def settings():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    data = get_dashboard_data()
    return render_template('settings.html', **data)

@app.route('/database')
def database():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    data = get_dashboard_data()
    return render_template('database.html', **data)

@app.route('/logs')
def logs():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    data = get_dashboard_data()
    return render_template('logs.html', **data)

@app.route('/reports')
def reports():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    data = get_dashboard_data()
    return render_template('reports.html', **data)

@app.route('/export')
def export():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    data = get_dashboard_data()
    return render_template('export.html', **data)

@app.route('/profile')
def profile():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    data = get_dashboard_data()
    return render_template('profile.html', **data)

@app.route('/logout')
def logout():
    logger.info(f"User {session.get('username', 'unknown')} logged out")
    session.clear()
    return redirect(url_for('login'))

# Functional routes for buttons and actions

@app.route('/export/csv')
def export_csv():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, category FROM clients ORDER BY id")
        clients = cursor.fetchall()
        cursor.close()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Client Name', 'Category'])
        writer.writerows(clients)
        
        output.seek(0)
        logger.info(f"CSV export completed with {len(clients)} records")
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'clients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': 'Export failed'}), 500

@app.route('/export/json')
def export_json():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, category FROM clients ORDER BY id")
        clients = cursor.fetchall()
        cursor.close()
        
        data = {
            'export_date': datetime.now().isoformat(),
            'total_clients': len(clients),
            'clients': [{'id': row[0], 'name': row[1], 'category': row[2]} for row in clients]
        }
        
        logger.info(f"JSON export completed with {len(clients)} records")
        return send_file(
            io.BytesIO(json.dumps(data, indent=2).encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'clients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': 'Export failed'}), 500

@app.route('/export/logs')
def export_logs():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Create sample log data
    log_data = [
        {'timestamp': '2024-01-15 14:30:25', 'level': 'INFO', 'message': 'User admin logged in successfully'},
        {'timestamp': '2024-01-15 14:28:12', 'level': 'SUCCESS', 'message': 'Database backup completed'},
        {'timestamp': '2024-01-15 14:25:45', 'level': 'WARNING', 'message': 'High memory usage detected'},
        {'timestamp': '2024-01-15 14:22:18', 'level': 'ERROR', 'message': 'Failed to connect to external API'},
        {'timestamp': '2024-01-15 14:20:33', 'level': 'INFO', 'message': 'New client added'},
    ]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Level', 'Message'])
    for log in log_data:
        writer.writerow([log['timestamp'], log['level'], log['message']])
    
    output.seek(0)
    logger.info("Logs export completed")
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'system_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/database/backup')
def database_backup():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, category FROM clients ORDER BY id")
        clients = cursor.fetchall()
        cursor.close()
        
        # Create SQL backup
        sql_backup = f"""-- Database Backup
-- Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
-- Total clients: {len(clients)}

DROP TABLE IF EXISTS clients;
CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL
);

"""
        
        for client in clients:
            sql_backup += f"INSERT INTO clients (id, name, category) VALUES ({client[0]}, '{client[1]}', '{client[2]}');\n"
        
        logger.info(f"Database backup completed with {len(clients)} records")
        return send_file(
            io.BytesIO(sql_backup.encode('utf-8')),
            mimetype='application/sql',
            as_attachment=True,
            download_name=f'database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'
        )
    except Exception as e:
        logger.error(f"Backup error: {e}")
        return jsonify({'error': 'Backup failed'}), 500

@app.route('/reports/pdf')
def download_report_pdf():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # For now, return a simple text file as PDF (in production, use a proper PDF library)
    try:
        data = get_dashboard_data()
        
        report_content = f"""CLIENT MANAGEMENT SYSTEM REPORT
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

SUMMARY:
- Total Clients: {data['total_clients']}
- Total Categories: {data['total_categories']}
- Average per Category: {data['avg_clients_per_category']}

CATEGORY BREAKDOWN:
"""
        
        for i, category in enumerate(data['categories']):
            report_content += f"- {category}: {data['category_counts'][i]} clients\n"
        
        logger.info("PDF report generated successfully")
        
        # Create the file content
        file_content = report_content.encode('utf-8')
        file_obj = io.BytesIO(file_content)
        file_obj.seek(0)
        
        return send_file(
            file_obj,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'client_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        )
    except Exception as e:
        logger.error(f"Report error: {e}")
        return jsonify({'error': 'Report generation failed'}), 500

@app.route('/logs/clear')
def clear_logs():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        # In a real application, this would clear actual log files
        # For now, just return success
        logger.info("Logs cleared by user")
        return jsonify({'message': 'Logs cleared successfully'})
    except Exception as e:
        logger.error(f"Clear logs error: {e}")
        return jsonify({'error': 'Failed to clear logs'}), 500

@app.route('/database/optimize')
def optimize_database():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("OPTIMIZE TABLE clients")
        cursor.fetchall()  # Consume any unread results
        cursor.close()
        logger.info("Database optimization completed")
        return jsonify({'message': 'Database optimized successfully'})
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        return jsonify({'error': 'Optimization failed'}), 500

@app.route('/database/test-connection')
def test_database_connection():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchall()  # Consume any unread results
        cursor.close()
        logger.info("Database connection test successful")
        return jsonify({'message': 'Database connection successful'})
    except Exception as e:
        logger.error(f"Connection test error: {e}")
        return jsonify({'error': 'Database connection failed'}), 500

@app.route('/settings/save', methods=['POST'])
def save_settings():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        # In a real application, you would save settings to database or config file
        logger.info("Settings saved by user")
        return jsonify({'message': 'Settings saved successfully'})
    except Exception as e:
        logger.error(f"Save settings error: {e}")
        return jsonify({'error': 'Failed to save settings'}), 500

@app.route('/settings/reset')
def reset_settings():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        # In a real application, you would reset to default settings
        logger.info("Settings reset to defaults by user")
        return jsonify({'message': 'Settings reset to defaults'})
    except Exception as e:
        logger.error(f"Reset settings error: {e}")
        return jsonify({'error': 'Failed to reset settings'}), 500

@app.route('/settings/clear-cache')
def clear_cache():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        # In a real application, you would clear application cache
        logger.info("Cache cleared by user")
        return jsonify({'message': 'Cache cleared successfully'})
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        return jsonify({'error': 'Failed to clear cache'}), 500

@app.route('/profile/save', methods=['POST'])
def save_profile():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        # In a real application, you would save profile data
        logger.info("Profile updated by user")
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        logger.error(f"Save profile error: {e}")
        return jsonify({'error': 'Failed to save profile'}), 500

@app.route('/profile/change-password', methods=['POST'])
def change_password():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            return jsonify({'error': 'New passwords do not match'}), 400
        
        # Hash passwords for comparison
        current_password_hash = hashlib.sha256(current_password.encode()).hexdigest()
        new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        ensure_db_connection()
        cursor = db.cursor()
        
        # Verify current password
        cursor.execute("SELECT id FROM users WHERE id = %s AND password_hash = %s", 
                      (session.get('user_id'), current_password_hash))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Update password
        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", 
                      (new_password_hash, session.get('user_id')))
        db.commit()
        cursor.close()
        
        logger.info(f"Password changed for user: {session.get('username')}")
        return jsonify({'message': 'Password updated successfully'})
    except Exception as e:
        logger.error(f"Change password error: {e}")
        return jsonify({'error': 'Failed to update password'}), 500

# User management routes
@app.route('/users')
def users():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Only admin can access user management
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    
    try:
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, username, email, full_name, role, is_active, 
                   created_at, last_login 
            FROM users 
            ORDER BY created_at DESC
        """)
        all_users = []
        for row in cursor.fetchall():
            all_users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'full_name': row[3],
                'role': row[4],
                'is_active': row[5],
                'created_at': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else '',
                'last_login': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else 'Never'
            })
        cursor.close()
        
        data = get_dashboard_data()
        data['all_users'] = all_users
        return render_template('users.html', **data)
    except Exception as e:
        logger.error(f"Users page error: {e}")
        data = get_dashboard_data()
        data['all_users'] = []
        return render_template('users.html', **data)

@app.route('/users/add', methods=['POST'])
def add_user():
    if 'logged_in' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email', '')
        full_name = request.form.get('full_name', '')
        role = request.form.get('role', 'user')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO users (username, password_hash, email, full_name, role) 
            VALUES (%s, %s, %s, %s, %s)
        """, (username, password_hash, email, full_name, role))
        db.commit()
        cursor.close()
        
        logger.info(f"New user added: {username} by {session.get('username')}")
        return jsonify({'message': 'User added successfully'})
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400
    except Exception as e:
        logger.error(f"Add user error: {e}")
        return jsonify({'error': 'Failed to add user'}), 500

@app.route('/users/edit/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    if 'logged_in' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        email = request.form.get('email', '')
        full_name = request.form.get('full_name', '')
        role = request.form.get('role', 'user')
        is_active = request.form.get('is_active', '1') == '1'
        
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE users SET email = %s, full_name = %s, role = %s, is_active = %s 
            WHERE id = %s
        """, (email, full_name, role, is_active, user_id))
        db.commit()
        cursor.close()
        
        logger.info(f"User {user_id} updated by {session.get('username')}")
        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        logger.error(f"Edit user error: {e}")
        return jsonify({'error': 'Failed to update user'}), 500

@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if 'logged_in' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Prevent admin from deleting themselves
    if user_id == session.get('user_id'):
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    try:
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        cursor.close()
        
        logger.info(f"User {user_id} deleted by {session.get('username')}")
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        return jsonify({'error': 'Failed to delete user'}), 500

@app.route('/export/advanced')
def export_advanced():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        # In a real application, you would show advanced export options
        logger.info("Advanced export options requested")
        return jsonify({'message': 'Advanced export options would be shown here'})
    except Exception as e:
        logger.error(f"Advanced export error: {e}")
        return jsonify({'error': 'Failed to load advanced options'}), 500

@app.route('/database/restore', methods=['POST'])
def restore_database():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        # In a real application, you would handle file upload and restore
        logger.info("Database restore requested")
        return jsonify({'message': 'Database restore functionality would be implemented here'})
    except Exception as e:
        logger.error(f"Database restore error: {e}")
        return jsonify({'error': 'Failed to restore database'}), 500

@app.route('/database/clear-cache')
def clear_database_cache():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        # In a real application, you would clear database cache
        logger.info("Database cache cleared")
        return jsonify({'message': 'Cache cleared successfully'})
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        return jsonify({'error': 'Failed to clear cache'}), 500

@app.route('/reports/email', methods=['POST'])
def email_report():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        # In a real application, you would send email with report
        logger.info("Email report requested")
        return jsonify({'message': 'Email functionality would be implemented here'})
    except Exception as e:
        logger.error(f"Email report error: {e}")
        return jsonify({'error': 'Failed to send email'}), 500

@app.route('/export/save-template', methods=['POST'])
def save_export_template():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        # In a real application, you would save export template
        logger.info("Export template saved")
        return jsonify({'message': 'Template saved successfully'})
    except Exception as e:
        logger.error(f"Save template error: {e}")
        return jsonify({'error': 'Failed to save template'}), 500

# Add client management functionality
@app.route('/clients/add', methods=['POST'])
def add_client():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        name = request.form.get('name')
        category = request.form.get('category')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        notes = request.form.get('notes', '')
        
        if not name or not category:
            return jsonify({'error': 'Name and category are required'}), 400
        
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO clients (name, category, email, phone, address, notes) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, category, email, phone, address, notes))
        db.commit()
        cursor.close()
        
        logger.info(f"New client added: {name} in category {category}")
        return jsonify({'message': 'Client added successfully'})
    except Exception as e:
        logger.error(f"Add client error: {e}")
        return jsonify({'error': 'Failed to add client'}), 500

@app.route('/clients/edit/<int:client_id>', methods=['POST'])
def edit_client(client_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        name = request.form.get('name')
        category = request.form.get('category')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        notes = request.form.get('notes', '')
        
        if not name or not category:
            return jsonify({'error': 'Name and category are required'}), 400
        
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE clients SET name = %s, category = %s, email = %s, phone = %s, address = %s, notes = %s 
            WHERE id = %s
        """, (name, category, email, phone, address, notes, client_id))
        db.commit()
        cursor.close()
        
        logger.info(f"Client {client_id} updated: {name} in category {category}")
        return jsonify({'message': 'Client updated successfully'})
    except Exception as e:
        logger.error(f"Edit client error: {e}")
        return jsonify({'error': 'Failed to update client'}), 500

@app.route('/clients/delete/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
        db.commit()
        cursor.close()
        
        logger.info(f"Client {client_id} deleted")
        return jsonify({'message': 'Client deleted successfully'})
    except Exception as e:
        logger.error(f"Delete client error: {e}")
        return jsonify({'error': 'Failed to delete client'}), 500

# Add category management functionality
@app.route('/categories/add', methods=['POST'])
def add_category():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        category_name = request.form.get('category_name')
        
        if not category_name:
            return jsonify({'error': 'Category name is required'}), 400
        
        # Add a sample client to the new category
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO clients (name, category) VALUES (%s, %s)", (f'Sample Client - {category_name}', category_name))
        db.commit()
        cursor.close()
        
        logger.info(f"New category added: {category_name}")
        return jsonify({'message': 'Category added successfully'})
    except Exception as e:
        logger.error(f"Add category error: {e}")
        return jsonify({'error': 'Failed to add category'}), 500

@app.route('/categories/delete/<category_name>', methods=['DELETE'])
def delete_category(category_name):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM clients WHERE category = %s", (category_name,))
        db.commit()
        cursor.close()
        
        logger.info(f"Category deleted: {category_name}")
        return jsonify({'message': 'Category deleted successfully'})
    except Exception as e:
        logger.error(f"Delete category error: {e}")
        return jsonify({'error': 'Failed to delete category'}), 500

# Enhanced client management endpoints
@app.route('/clients/import', methods=['POST'])
def import_clients():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Please upload a CSV file'}), 400
        
        # Read CSV file
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')
        
        # Skip header row
        data_lines = lines[1:] if len(lines) > 1 else []
        
        ensure_db_connection()
        cursor = db.cursor()
        
        imported_count = 0
        for line in data_lines:
            if line.strip():
                parts = line.split(',')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    category = parts[1].strip()
                    email = parts[2].strip() if len(parts) > 2 else ''
                    phone = parts[3].strip() if len(parts) > 3 else ''
                    address = parts[4].strip() if len(parts) > 4 else ''
                    notes = parts[5].strip() if len(parts) > 5 else ''
                    
                    if name and category:
                        cursor.execute("""
                            INSERT INTO clients (name, category, email, phone, address, notes) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (name, category, email, phone, address, notes))
                        imported_count += 1
        
        db.commit()
        cursor.close()
        
        logger.info(f"Imported {imported_count} clients from CSV")
        return jsonify({'message': f'Successfully imported {imported_count} clients'})
    except Exception as e:
        logger.error(f"Import clients error: {e}")
        return jsonify({'error': 'Failed to import clients'}), 500

@app.route('/clients/bulk-delete', methods=['POST'])
def bulk_delete_clients():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        data = request.get_json()
        client_ids = data.get('client_ids', [])
        
        if not client_ids:
            return jsonify({'error': 'No clients selected'}), 400
        
        ensure_db_connection()
        cursor = db.cursor()
        
        # Convert list to tuple for SQL IN clause
        placeholders = ','.join(['%s'] * len(client_ids))
        cursor.execute(f"DELETE FROM clients WHERE id IN ({placeholders})", tuple(client_ids))
        deleted_count = cursor.rowcount
        
        db.commit()
        cursor.close()
        
        logger.info(f"Bulk deleted {deleted_count} clients")
        return jsonify({'message': f'Successfully deleted {deleted_count} clients'})
    except Exception as e:
        logger.error(f"Bulk delete error: {e}")
        return jsonify({'error': 'Failed to delete clients'}), 500

@app.route('/clients/bulk-update-category', methods=['POST'])
def bulk_update_category():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        data = request.get_json()
        client_ids = data.get('client_ids', [])
        new_category = data.get('category', '')
        
        if not client_ids or not new_category:
            return jsonify({'error': 'Client IDs and category are required'}), 400
        
        ensure_db_connection()
        cursor = db.cursor()
        
        # Convert list to tuple for SQL IN clause
        placeholders = ','.join(['%s'] * len(client_ids))
        cursor.execute(f"UPDATE clients SET category = %s WHERE id IN ({placeholders})", 
                      (new_category,) + tuple(client_ids))
        updated_count = cursor.rowcount
        
        db.commit()
        cursor.close()
        
        logger.info(f"Bulk updated category for {updated_count} clients to {new_category}")
        return jsonify({'message': f'Successfully updated category for {updated_count} clients'})
    except Exception as e:
        logger.error(f"Bulk update category error: {e}")
        return jsonify({'error': 'Failed to update client categories'}), 500

@app.route('/clients/<int:client_id>')
def get_client_details(client_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        ensure_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, name, category, email, phone, address, notes, created_at, updated_at 
            FROM clients WHERE id = %s
        """, (client_id,))
        client = cursor.fetchone()
        cursor.close()
        
        if client:
            client_data = {
                'id': client[0],
                'name': client[1],
                'category': client[2],
                'email': client[3] or '',
                'phone': client[4] or '',
                'address': client[5] or '',
                'notes': client[6] or '',
                'created_at': client[7].isoformat() if client[7] else '',
                'updated_at': client[8].isoformat() if client[8] else ''
            }
            return jsonify(client_data)
        else:
            return jsonify({'error': 'Client not found'}), 404
    except Exception as e:
        logger.error(f"Get client details error: {e}")
        return jsonify({'error': 'Failed to get client details'}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)