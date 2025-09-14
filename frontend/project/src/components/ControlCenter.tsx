import React from 'react';
import { motion } from 'framer-motion';

interface ControlCenterProps {
  permissions: Record<string, boolean>;
  togglePermission: (key: string) => void;
}

const ControlCenter: React.FC<ControlCenterProps> = ({ permissions, togglePermission }) => {
  const permissionLabels = {
    assets: 'Assets',
    liabilities: 'Liabilities', 
    transactions: 'Transactions',
    investments: 'Investments',
    epfBalance: 'EPF Balance',
    creditScore: 'Credit Score'
  };

  const ToggleSwitch = ({ isOn, onToggle }: { isOn: boolean; onToggle: () => void }) => (
    <motion.button
      className={`relative inline-flex h-6 w-11 rounded-full transition-colors ${
        isOn ? 'bg-[#00D1B2]' : 'bg-[#0A0F1F]'
      }`}
      onClick={onToggle}
      whileTap={{ scale: 0.95 }}
    >
      <motion.span
        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-lg transition-transform ${
          isOn ? 'translate-x-6' : 'translate-x-1'
        } my-1`}
        animate={{ x: isOn ? 24 : 4 }}
        transition={{ type: "spring", stiffness: 700, damping: 30 }}
      />
    </motion.button>
  );

  return (
    <div className="bg-[#10182F] backdrop-blur-sm rounded-2xl p-6 border border-[#00D1B2]/20 h-[calc(100vh-140px)]">
      <h2 className="text-xl font-semibold text-white mb-6">Data Permissions</h2>
      
      <div className="space-y-4">
        {Object.entries(permissionLabels).map(([key, label]) => (
          <div key={key} className="flex items-center justify-between">
            <span className="text-[#A0AEC0] text-sm">{label}</span>
            <ToggleSwitch 
              isOn={permissions[key]}
              onToggle={() => togglePermission(key)}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default ControlCenter;