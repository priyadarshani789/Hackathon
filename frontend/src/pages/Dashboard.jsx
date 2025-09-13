import { useState, useEffect } from "react";
import Layout from "../components/layout/Layout";
import StatCard from "../components/StatCard";
import UploadBox from "../components/UploadBox";
import { AlertTriangle, FileText, CheckCircle, ChevronDown } from "lucide-react";

export default function Dashboard() {
  const [stats, setStats] = useState({
    documentsUploaded: 0,
    complianceScore: "--",
    issuesFound: "--"
  });
  
  const [showTips, setShowTips] = useState(false);
  const [loading, setLoading] = useState(false);

  // Handle file upload from UploadBox
  const handleFilesUploaded = (fileCount) => {
    setLoading(true);
    
    // Simulate API processing
    setTimeout(() => {
      setStats({
        documentsUploaded: stats.documentsUploaded + fileCount,
        complianceScore: Math.floor(Math.random() * 100) + "%",
        issuesFound: Math.floor(Math.random() * 10)
      });
      setLoading(false);
    }, 2000);
  };

  return (
    <Layout>
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-6 mb-6 text-white shadow-lg">
        <h2 className="text-2xl font-bold mb-2">Welcome to Compliance Assistant</h2>
        <p className="opacity-90 mb-4">Upload your documents to check GxP compliance and regulatory standards.</p>
        
        <div className="mt-2">
          <button 
            onClick={() => setShowTips(!showTips)} 
            className="flex items-center text-sm font-medium bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg px-3 py-1 transition-all"
          >
            {showTips ? "Hide Tips" : "Show Tips"}
            <ChevronDown 
              size={16} 
              className={`ml-1 transition-transform ${showTips ? "rotate-180" : ""}`} 
            />
          </button>
        </div>
        
        {showTips && (
          <div className="mt-3 p-3 bg-white bg-opacity-10 rounded-lg animate-fadeIn">
            <ul className="list-disc list-inside text-sm space-y-1">
              <li>Upload PDF or Word documents for best results</li>
              <li>Multiple files can be analyzed in one batch</li>
              <li>Results are available immediately after processing</li>
            </ul>
          </div>
        )}
      </div>

     

      {/* Upload Section */}
      <UploadBox onFilesUploaded={handleFilesUploaded} />
      
      {/* Recent Activity */}
      {stats.documentsUploaded > 0 && (
        <div className="mt-8 bg-white p-6 rounded-xl border shadow-sm animate-slideUp">
          <h3 className="font-medium text-gray-800 mb-3">Recent Activity</h3>
          <div className="space-y-2">
            <div className="flex items-center p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 rounded-full bg-green-500 mr-3"></div>
              <p className="text-sm">Document analysis completed</p>
              <span className="text-xs text-gray-500 ml-auto">Just now</span>
            </div>
            {stats.issuesFound > 0 && (
              <div className="flex items-center p-3 bg-gray-50 rounded-lg">
                <div className="w-2 h-2 rounded-full bg-yellow-500 mr-3"></div>
                <p className="text-sm">{stats.issuesFound} compliance issues detected</p>
                <span className="text-xs text-gray-500 ml-auto">Just now</span>
              </div>
            )}
          </div>
        </div>
      )}
       {/* Stats Section with conditional animation */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <StatCard
          title="Documents Uploaded"
          value={stats.documentsUploaded}
          subtitle="Ready for analysis"
          icon={<FileText size={18} />}
          highlight={stats.documentsUploaded > 0}
        />
       
       
      </div>
    </Layout>
  );
}