import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  UserCircleIcon, 
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  ChartBarIcon,
  DocumentArrowUpIcon,
  HomeIcon,
  EnvelopeIcon,
  DevicePhoneMobileIcon,
  UserIcon,
  XMarkIcon as CloseIcon
} from '@heroicons/react/24/outline';

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const ProfileModal = () => {
    if (!isProfileModalOpen) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Profile Information</h2>
            <button
              onClick={() => setIsProfileModalOpen(false)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <CloseIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Profile Content */}
          <div className="p-6">
            {/* Profile Avatar */}
            <div className="flex justify-center mb-6">
              <div className="relative">
                <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <UserIcon className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-white"></div>
              </div>
            </div>

            {/* User Information */}
            <div className="space-y-4">
              {/* Full Name */}
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <UserIcon className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-500">Full Name</p>
                  <p className="font-semibold text-gray-900">{user?.full_name || 'Not provided'}</p>
                </div>
              </div>

              {/* Username */}
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <UserCircleIcon className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-500">Username</p>
                  <p className="font-semibold text-gray-900">{user?.username || 'Not provided'}</p>
                </div>
              </div>

              {/* Email */}
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <EnvelopeIcon className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-500">Email Address</p>
                  <p className="font-semibold text-gray-900">{user?.email || 'Not provided'}</p>
                </div>
              </div>

              {/* Mobile Number */}
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <DevicePhoneMobileIcon className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-500">Mobile Number</p>
                  <p className="font-semibold text-gray-900">{user?.mobile_number || 'Not provided'}</p>
                </div>
              </div>

              {/* Account Status */}
              <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Account Status</p>
                  <p className="font-semibold text-green-700">Active</p>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-6 space-y-3">
              <button
                onClick={() => {
                  setIsProfileModalOpen(false);
                  // You can add edit profile functionality here
                }}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105"
              >
                Edit Profile
              </button>
              <button
                onClick={() => {
                  setIsProfileModalOpen(false);
                  handleLogout();
                }}
                className="w-full border border-red-300 text-red-600 py-3 px-4 rounded-lg font-semibold hover:bg-red-50 transition-all duration-300"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <>
      <nav className="bg-white/80 backdrop-blur-xl shadow-lg border-b border-white/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-3 group">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl blur-lg opacity-30 group-hover:opacity-50 transition-opacity"></div>
                  <div className="relative bg-white p-2 rounded-xl shadow-lg">
                    <div className="h-8 w-8">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="url(#gradient)" className="h-8 w-8">
                        <defs>
                          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" style={{stopColor: '#2563eb', stopOpacity: 1}} />
                            <stop offset="100%" style={{stopColor: '#9333ea', stopOpacity: 1}} />
                          </linearGradient>
                        </defs>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 0 1 4.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0 1 12 15a9.065 9.065 0 0 0-6.23-.693L5 14.5m14.8.8 1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0 1 12 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                      </svg>
                    </div>
                  </div>
                </div>
                <div className="hidden sm:block">
                  <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    BloodReport AI
                  </span>
                </div>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-1">
              {isAuthenticated ? (
                <>
                  <Link
                    to="/dashboard"
                    className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:text-blue-600 rounded-xl text-sm font-medium transition-all duration-300 hover:bg-blue-50 group"
                  >
                    <ChartBarIcon className="h-5 w-5 group-hover:scale-110 transition-transform" />
                    <span>Dashboard</span>
                  </Link>
                  <Link
                    to="/upload"
                    className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:text-blue-600 rounded-xl text-sm font-medium transition-all duration-300 hover:bg-blue-50 group"
                  >
                    <DocumentArrowUpIcon className="h-5 w-5 group-hover:scale-110 transition-transform" />
                    <span>Upload Report</span>
                  </Link>
                  
                  {/* User Menu */}
                  <div className="flex items-center space-x-4 ml-4 pl-4 border-l border-gray-200">
                    <button
                      onClick={() => setIsProfileModalOpen(true)}
                      className="flex items-center space-x-3 bg-gradient-to-r from-blue-50 to-purple-50 px-4 py-2 rounded-xl hover:from-blue-100 hover:to-purple-100 transition-all duration-300 cursor-pointer group"
                    >
                      <UserCircleIcon className="h-6 w-6 text-blue-600 group-hover:scale-110 transition-transform" />
                      <div className="text-sm">
                        <p className="font-semibold text-gray-900">{user?.full_name || user?.username}</p>
                        <p className="text-xs text-gray-500">Click to view profile</p>
                      </div>
                    </button>
                    <button
                      onClick={handleLogout}
                      className="flex items-center space-x-2 text-gray-700 hover:text-red-600 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-300 hover:bg-red-50 group"
                    >
                      <ArrowRightOnRectangleIcon className="h-5 w-5 group-hover:scale-110 transition-transform" />
                      <span>Logout</span>
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="px-4 py-2 text-gray-700 hover:text-blue-600 rounded-xl text-sm font-medium transition-all duration-300 hover:bg-blue-50"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-2 rounded-xl text-sm font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                  >
                    Get Started
                  </Link>
                </>
              )}
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden flex items-center">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-gray-700 hover:text-blue-600 p-2 rounded-xl transition-all duration-300 hover:bg-blue-50"
              >
                {isMenuOpen ? (
                  <XMarkIcon className="h-6 w-6" />
                ) : (
                  <Bars3Icon className="h-6 w-6" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden bg-white/95 backdrop-blur-xl border-t border-white/20 slide-in">
            <div className="px-4 pt-2 pb-6 space-y-2">
              {isAuthenticated ? (
                <>
                  <Link
                    to="/dashboard"
                    className="flex items-center space-x-3 text-gray-700 hover:text-blue-600 px-4 py-3 rounded-xl text-base font-medium transition-all duration-300 hover:bg-blue-50"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <ChartBarIcon className="h-6 w-6" />
                    <span>Dashboard</span>
                  </Link>
                  <Link
                    to="/upload"
                    className="flex items-center space-x-3 text-gray-700 hover:text-blue-600 px-4 py-3 rounded-xl text-base font-medium transition-all duration-300 hover:bg-blue-50"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <DocumentArrowUpIcon className="h-6 w-6" />
                    <span>Upload Report</span>
                  </Link>
                  
                  {/* Mobile User Info */}
                  <div className="border-t border-gray-200 pt-4 mt-4">
                    <button
                      onClick={() => {
                        setIsMenuOpen(false);
                        setIsProfileModalOpen(true);
                      }}
                      className="w-full bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 mb-4 hover:from-blue-100 hover:to-purple-100 transition-all duration-300"
                    >
                      <div className="flex items-center space-x-3">
                        <UserCircleIcon className="h-8 w-8 text-blue-600" />
                        <div className="text-left">
                          <p className="font-semibold text-gray-900">{user?.full_name || user?.username}</p>
                          <p className="text-sm text-gray-500">Tap to view profile</p>
                        </div>
                      </div>
                    </button>
                    <button
                      onClick={() => {
                        handleLogout();
                        setIsMenuOpen(false);
                      }}
                      className="flex items-center space-x-3 text-gray-700 hover:text-red-600 w-full px-4 py-3 rounded-xl text-base font-medium transition-all duration-300 hover:bg-red-50"
                    >
                      <ArrowRightOnRectangleIcon className="h-6 w-6" />
                      <span>Logout</span>
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="flex items-center space-x-3 text-gray-700 hover:text-blue-600 px-4 py-3 rounded-xl text-base font-medium transition-all duration-300 hover:bg-blue-50"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <HomeIcon className="h-6 w-6" />
                    <span>Login</span>
                  </Link>
                  <Link
                    to="/register"
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center justify-center px-4 py-3 rounded-xl text-base font-semibold transition-all duration-300 shadow-lg"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Get Started
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Profile Modal */}
      <ProfileModal />
    </>
  );
};

export default Navbar; 