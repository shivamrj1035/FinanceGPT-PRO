import React from 'react';
import { motion } from 'framer-motion';
import ControlCenter from './ControlCenter';
import DataGrid from './DataGrid';
import AIAssistant from './AIAssistant';

interface DashboardProps {
  permissions: Record<string, boolean>;
  togglePermission: (key: string) => void;
  chatHistory: Array<{ sender: string; content: string }>;
  addChatMessage: (sender: string, content: string) => void;
  onLogout: () => void;
  currentUser?: { user_id: string; email: string } | null;
}

const Dashboard: React.FC<DashboardProps> = ({
  permissions,
  togglePermission,
  chatHistory,
  addChatMessage,
  onLogout,
  currentUser
}) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen bg-[#0A0F1F]"
    >
      {/* Header */}
      <header className="flex justify-between items-center p-6 border-b border-[#00D1B2]/20">
        <h1 className="text-2xl font-bold text-white">Finara</h1>
        <button
          onClick={onLogout}
          className="px-4 py-2 bg-[#10182F] text-[#A0AEC0] rounded-lg hover:bg-[#8A2BE2] hover:text-white transition-all"
        >
          Logout
        </button>
      </header>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-12 gap-6 p-6 min-h-[calc(100vh-88px)]">
        {/* Left Column - Control Center */}
        <div className="col-span-12 lg:col-span-3">
          <ControlCenter 
            permissions={permissions}
            togglePermission={togglePermission}
          />
        </div>

        {/* Center Column - Data Grid */}
        <div className="col-span-12 lg:col-span-6">
          <DataGrid permissions={permissions} currentUser={currentUser} />
        </div>

        {/* Right Column - AI Assistant */}
        <div className="col-span-12 lg:col-span-3">
          <AIAssistant
            permissions={permissions}
            chatHistory={chatHistory}
            addChatMessage={addChatMessage}
            currentUser={currentUser}
          />
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;