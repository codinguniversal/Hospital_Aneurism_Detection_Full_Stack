<template>
  <div class="card-container">
    <div class="page-header">
      <h1>User Profile</h1>
      <p>Manage your account settings and preferences</p>
    </div>

    <div class="profile-content">
      <div class="profile-sidebar">
        <div class="avatar-circle">
          <i class="fa fa-user-md"></i>
        </div>
        <h2 class="user-name">{{ authStore.userName || 'Medical Professional' }}</h2>
        <span class="role-badge">Lead Diagnostician</span>
      </div>

      <div class="profile-details">
        <h3>Account Information</h3>
        
        <div class="info-group">
          <label>Full Name</label>
          <div class="info-value">{{ authStore.userName || 'Not provided' }}</div>
        </div>

        <div class="info-group">
          <label>Email Address</label>
          <div class="info-value">dr.{{ authStore.userName.toLowerCase().replace(/\s+/g, '') || 'user' }}@hospital.org</div>
        </div>

        <div class="info-group">
          <label>Department</label>
          <div class="info-value">Neurology & Radiology</div>
        </div>

        <div class="profile-actions">
          <button class="action-btn btn-outline-green">Edit Profile</button>
          <button class="action-btn btn-grey">Change Password</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { authStore } from '../store.js'
</script>

<style scoped>
/* Reusing the white card styles */
.card-container {
  background: #ffffff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 800px;
}

.page-header { margin-bottom: 25px; border-bottom: 2px solid #f0f2f5; padding-bottom: 15px; }
.page-header h1 { color: #2c3e50; font-size: 28px; margin-bottom: 5px; }
.page-header p { color: #7f8c8d; font-size: 15px; }

.profile-content {
  display: flex;
  gap: 40px;
  margin-top: 30px;
}

/* Sidebar Layout */
.profile-sidebar {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 200px;
  border-right: 2px solid #f0f2f5;
  padding-right: 40px;
}

.avatar-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: #e8f5e9;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
  border: 4px solid #ffffff;
  box-shadow: 0 4px 10px rgba(10, 161, 89, 0.15);
}

.avatar-circle i {
  font-size: 50px;
  color: #0aa159;
}

.user-name {
  color: #2c3e50;
  font-size: 20px;
  margin-bottom: 5px;
  text-align: center;
}

.role-badge {
  background: #f1f3f5;
  color: #5c6bc0;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

/* Details Layout */
.profile-details {
  flex: 1;
}

.profile-details h3 {
  color: #34495e;
  font-size: 18px;
  margin-bottom: 20px;
}

.info-group {
  margin-bottom: 20px;
}

.info-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #7f8c8d;
  margin-bottom: 5px;
  text-transform: uppercase;
}

.info-value {
  font-size: 16px;
  color: #2c3e50;
  padding: 10px 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.profile-actions {
  margin-top: 35px;
  display: flex;
  gap: 15px;
}

/* Buttons */
.btn-outline-green { background: transparent; color: #0aa159; border: 1px solid #0aa159; }
.btn-outline-green:hover { background: #e8f5e9; transform: translateY(-2px); }
.btn-grey { background: #f1f3f5; color: #495057; border: none; }
.btn-grey:hover { background: #e9ecef; transform: translateY(-2px); }
</style>