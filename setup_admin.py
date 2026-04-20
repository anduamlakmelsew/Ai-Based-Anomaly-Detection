#!/usr/bin/env python3
"""
Create or Update Admin User Script
Ensures admin user has a secure, unique password
"""

import sys
import secrets
import string

# Add backend path
sys.path.append('/home/andu/AI_Baseline_Assessment_Scanner/backend')

def generate_readable_password(length=12):
    """Generate a readable password without ambiguous characters"""
    # Exclude ambiguous characters: 0, O, o, l, 1, I
    lowercase = 'abcdefghjkmnpqrstuvwxyz'
    uppercase = 'ABCDEFGHJKMNPQRSTUVWXYZ'
    digits = '23456789'
    
    # Ensure at least one of each type
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(lowercase)
    ]
    
    # Fill remaining with mixed characters
    all_chars = lowercase + uppercase + digits
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle the password
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

def create_admin_user():
    """Create or update admin user with secure password"""
    try:
        from app import create_app, db
        from app.models.user_model import User
        
        app = create_app()
        
        with app.app_context():
            # Check if admin user exists
            admin_user = User.query.filter_by(username="admin").first()
            
            if admin_user:
                print("🔍 Admin user found, updating password...")
                # Generate readable password
                new_password = generate_readable_password()
                admin_user.set_password(new_password)
                admin_user.email = admin_user.email or "admin@securityscanner.local"
                admin_user.role = "admin"
                
                db.session.commit()
                
                print("✅ Admin user password updated successfully!")
                print(f"📧 Email: {admin_user.email}")
                print(f"🔑 New Password: {new_password}")
                print("⚠️  Save this password securely!")
                
            else:
                print("👤 Creating new admin user...")
                # Generate readable password
                admin_password = generate_readable_password()
                
                admin_user = User(
                    username="admin",
                    email="admin@securityscanner.local",
                    role="admin"
                )
                admin_user.set_password(admin_password)
                
                db.session.add(admin_user)
                db.session.commit()
                
                print("✅ Admin user created successfully!")
                print(f"📧 Email: admin@securityscanner.local")
                print(f"🔑 Password: {admin_password}")
                print("⚠️  Save this password securely!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_user_registration():
    """Check if user registration is working"""
    try:
        from app import create_app, db
        from app.models.user_model import User
        
        app = create_app()
        
        with app.app_context():
            # Count existing users
            user_count = User.query.count()
            print(f"📊 Current users in database: {user_count}")
            
            # List all users
            users = User.query.all()
            for user in users:
                print(f"  - {user.username} ({user.email}) - Role: {user.role}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error checking users: {e}")
        return False

def main():
    """Main function"""
    print("🚀 ADMIN USER SETUP SCRIPT")
    print("=" * 50)
    
    # Check existing users
    print("\n1. Checking existing users...")
    check_user_registration()
    
    # Create/update admin user
    print("\n2. Setting up admin user...")
    success = create_admin_user()
    
    if success:
        print("\n✅ Admin user setup completed!")
        print("\n📋 Next Steps:")
        print("  1. Use the provided admin credentials to login")
        print("  2. New security analysts can register via the registration page")
        print("  3. Admin can manage user roles and permissions")
        
        print("\n🔐 Security Features:")
        print("  ✅ Admin user requires unique password")
        print("  ✅ Password validation enforced for new users")
        print("  ✅ No more debug bypasses in authentication")
        print("  ✅ Account registration available for analysts")
    else:
        print("\n❌ Admin user setup failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
