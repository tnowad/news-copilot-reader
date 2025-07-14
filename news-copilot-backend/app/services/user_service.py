from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.user import User
from app.models.role import Role, RoleEnum
from app.services.base_service import BaseService
from app.extensions import db, bcrypt


class UserService(BaseService):
    """Enhanced service for user operations"""
    
    def __init__(self):
        super().__init__(User)
    
    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user with enhanced validation"""
        try:
            # Validate required fields
            if not data.get('email'):
                return self._format_error_response(400, "Email is required")
            
            if not data.get('password'):
                return self._format_error_response(400, "Password is required")
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return self._format_error_response(400, "Email is already registered")
            
            # Validate password strength
            password_validation = self._validate_password(data['password'])
            if not password_validation['valid']:
                return self._format_error_response(400, "Invalid password", password_validation['errors'])
            
            # Create user
            user = User(
                email=data['email'],
                display_name=data.get('displayName'),
                avatar_image=data.get('avatarImage'),
                phone_number=data.get('phoneNumber'),
                bio=data.get('bio'),
                birth_date=datetime.strptime(data['birthDate'], '%Y-%m-%d') if data.get('birthDate') else None
            )
            
            # Set password
            user.set_password(data['password'])
            
            # Assign default role
            default_role = Role.query.filter_by(name=RoleEnum.USER).first()
            if default_role:
                user.roles.append(default_role)
            
            db.session.add(user)
            db.session.commit()
            
            return self._format_response(
                201,
                "User created successfully",
                self._serialize(user)
            )
            
        except Exception as e:
            db.session.rollback()
            return self._format_error_response(500, "Failed to create user", str(e))
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with enhanced security checks"""
        try:
            if not email or not password:
                return self._format_error_response(400, "Email and password are required")
            
            user = User.query.filter_by(email=email).first()
            
            if not user:
                return self._format_error_response(401, "Invalid email or password")
            
            if not user.check_password(password):
                return self._format_error_response(401, "Invalid email or password")
            
            # Check if user is active (not soft deleted)
            if user.deleted_at:
                return self._format_error_response(401, "Account is deactivated")
            
            return self._format_response(
                200,
                "Authentication successful",
                {
                    "user": self._serialize(user),
                    "roles": [str(role.name) for role in user.roles]
                }
            )
            
        except Exception as e:
            return self._format_error_response(500, "Authentication failed", str(e))
    
    def update_profile(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile with validation"""
        try:
            user = User.query.get(user_id)
            if not user:
                return self._format_error_response(404, "User not found")
            
            # Update allowed fields
            allowed_fields = ['display_name', 'avatar_image', 'phone_number', 'bio', 'birth_date']
            
            for field in allowed_fields:
                if field in data:
                    if field == 'birth_date' and data[field]:
                        try:
                            user.birth_date = datetime.strptime(data[field], '%Y-%m-%d')
                        except ValueError:
                            return self._format_error_response(400, "Invalid birth date format. Use YYYY-MM-DD")
                    else:
                        setattr(user, field, data[field])
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return self._format_response(
                200,
                "Profile updated successfully",
                self._serialize(user)
            )
            
        except Exception as e:
            db.session.rollback()
            return self._format_error_response(500, "Failed to update profile", str(e))
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password with validation"""
        try:
            user = User.query.get(user_id)
            if not user:
                return self._format_error_response(404, "User not found")
            
            # Verify current password
            if not user.check_password(current_password):
                return self._format_error_response(400, "Current password is incorrect")
            
            # Validate new password
            password_validation = self._validate_password(new_password)
            if not password_validation['valid']:
                return self._format_error_response(400, "Invalid new password", password_validation['errors'])
            
            # Update password
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return self._format_response(200, "Password changed successfully")
            
        except Exception as e:
            db.session.rollback()
            return self._format_error_response(500, "Failed to change password", str(e))
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            user = User.query.get(user_id)
            if not user:
                return self._format_error_response(404, "User not found")
            
            stats = {
                "articlesCount": len(user.articles),
                "commentsCount": len(user.comments),
                "bookmarksCount": len(user.bookmarks),
                "viewsCount": len(user.views),
                "memberSince": user.created_at.isoformat() if user.created_at else None
            }
            
            return self._format_response(
                200,
                "User statistics retrieved successfully",
                {"stats": stats}
            )
            
        except Exception as e:
            return self._format_error_response(500, "Failed to retrieve user statistics", str(e))
    
    def _validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _serialize(self, user: User, include_sensitive: bool = False) -> Dict[str, Any]:
        """Serialize user to dictionary"""
        data = {
            "id": user.id,
            "email": user.email,
            "displayName": user.display_name,
            "avatarImage": user.avatar_image,
            "createdAt": user.created_at.isoformat() if user.created_at else None,
            "updatedAt": user.updated_at.isoformat() if user.updated_at else None
        }
        
        if include_sensitive:
            data.update({
                "phoneNumber": user.phone_number,
                "bio": user.bio,
                "birthDate": user.birth_date.strftime('%Y-%m-%d') if user.birth_date else None,
                "roles": [str(role.name) for role in user.roles]
            })
        
        return data
