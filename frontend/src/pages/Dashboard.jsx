import { useState, useEffect } from "react";
import Layout from "../components/layout/Layout";
import StatCard from "../components/StatCard";
import UploadBox from "../components/UploadBox";
import { AlertTriangle, FileText, CheckCircle, ChevronDown } from "lucide-react";

export default function Dashboard() {
  const [stats, setStats] = useState({
    documentsUploaded: 0,
    complianceScore: "--",
    issuesFound: "--",
    chunksStored: 0
  });
  
  const [showTips, setShowTips] = useState(false);
  const [loading, setLoading] = useState(false);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [apiHealth, setApiHealth] = useState(null);
  const [dbStats, setDbStats] = useState(null);

  // Check API health on component mount
  useEffect(() => {
    checkApiHealth();
    fetchDbStats();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch('/health');
      if (response.ok) {
        const health = await response.json();
        setApiHealth(health);
      }
    } catch (error) {
      console.error('API health check failed:', error);
      setApiHealth({ status: 'error' });
    }
  };

  const fetchDbStats = async () => {
    try {
      const response = await fetch('/api/documents/stats');
      if (response.ok) {
        const data = await response.json();
        setDbStats(data.stats);
      }
    } catch (error) {
      console.error('Failed to fetch database stats:', error);
    }
  };

  // Handle analysis results from UploadBox
  const handleAnalysisResults = (results) => {
    setLoading(true);
    
    // Process the results from the backend
    setTimeout(() => {
      setAnalysisResults(results);
      
      // Calculate aggregate stats
      const totalFiles = results.length;
      const averageScore = results.reduce((sum, result) => sum + result.score, 0) / totalFiles;
      const totalIssues = results.reduce((sum, result) => sum + result.findings.length, 0);
      const totalChunks = results.reduce((sum, result) => {
        return sum + (result.embedding_info?.chunks_stored || 0);
      }, 0);
      
      setStats(prevStats => ({
        documentsUploaded: prevStats.documentsUploaded + totalFiles,
        complianceScore: Math.round(averageScore) + "%",
        issuesFound: totalIssues,
        chunksStored: prevStats.chunksStored + totalChunks
      }));
      setLoading(false);
      
      // Refresh database stats
      fetchDbStats();
    }, 1000);
  };

  return (
    <Layout>
      {/* API Status Banner */}
      {apiHealth && apiHealth.status === 'error' && (
        <div className="bg-red-100 border border-red-300 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
            <p className="text-red-700 text-sm">
              ⚠️ Backend API is not available. Please check if the server is running.
            </p>
          </div>
        </div>
      )}

      {/* Database Stats Banner */}
      {dbStats && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <FileText className="h-5 w-5 text-blue-500 mr-2" />
              <div>
                <p className="text-blue-800 text-sm font-medium">
                  Document Database: {dbStats.unique_documents} documents, {dbStats.total_chunks} chunks stored
                </p>
                <p className="text-blue-600 text-xs">
                  Ready for semantic search and compliance analysis
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-6 mb-6 text-white shadow-lg">
        <h2 className="text-2xl font-bold mb-2">Welcome to GxP Compliance Assistant</h2>
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
              <li>Upload PDF or DOCX documents for best results</li>
              <li>Multiple files can be analyzed in one batch</li>
              <li>Results include compliance scores and detailed findings</li>
              <li>Documents are processed using AI for comprehensive analysis</li>
            </ul>
          </div>
        )}
      </div>

      {/* Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <StatCard
          title="Documents Uploaded"
          value={stats.documentsUploaded}
          subtitle="Ready for analysis"
          icon={<FileText size={18} />}
          highlight={stats.documentsUploaded > 0}
        />
        <StatCard
          title="Compliance Score"
          value={stats.complianceScore}
          subtitle="Average across all docs"
          icon={<CheckCircle size={18} />}
          highlight={stats.complianceScore !== "--"}
        />
        <StatCard
          title="Issues Found"
          value={stats.issuesFound}
          subtitle="Requiring attention"
          icon={<AlertTriangle size={18} />}
          highlight={stats.issuesFound !== "--"}
        />
      </div>

      {/* Upload Section */}
      <UploadBox onFilesUploaded={handleAnalysisResults} />
      
      {/* Analysis Results */}
      {analysisResults.length > 0 && (
        <div className="mt-8 bg-white p-6 rounded-xl border shadow-sm animate-slideUp">
          <h3 className="font-medium text-gray-800 mb-4">Analysis Results</h3>
          <div className="space-y-4">
            {analysisResults.map((result, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">{result.filename}</h4>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                    result.score >= 80 ? 'bg-green-100 text-green-800' :
                    result.score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    Compliance Score: {result.score}%
                  </div>
                </div>
                
                {/* Document Info */}
                {result.document_info && (
                  <div className="mb-3 p-2 bg-gray-50 rounded text-sm">
                    <p><strong>Sections Found:</strong> {result.document_info.sections_found}</p>
                    {result.embedding_info && (
                      <p><strong>Chunks Stored:</strong> {result.embedding_info.chunks_stored || 0}</p>
                    )}
                  </div>
                )}
                
                {result.findings && result.findings.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-gray-700">
                      Compliance Issues ({result.findings.length}):
                    </p>
                    
                    {/* Group findings by category */}
                    {(() => {
                      const grouped = result.findings.reduce((acc, finding) => {
                        const category = finding.category || 'General';
                        if (!acc[category]) acc[category] = [];
                        acc[category].push(finding);
                        return acc;
                      }, {});
                      
                      return Object.entries(grouped).map(([category, findings]) => (
                        <div key={category} className="mb-3">
                          <h5 className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">
                            {category} ({findings.length})
                          </h5>
                          <div className="space-y-1">
                            {findings.slice(0, 3).map((finding, findingIndex) => (
                              <div key={findingIndex} className={`flex items-start p-2 rounded text-sm ${
                                finding.severity === 'Critical' ? 'bg-red-50 border-l-4 border-red-400 text-red-800' :
                                finding.severity === 'Major' ? 'bg-yellow-50 border-l-4 border-yellow-400 text-yellow-800' :
                                'bg-blue-50 border-l-4 border-blue-400 text-blue-800'
                              }`}>
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="font-medium">{finding.severity}</span>
                                    <span className="text-xs bg-white px-1 rounded">
                                      {finding.rule_id || 'GXP'}
                                    </span>
                                  </div>
                                  <p>{finding.description}</p>
                                  {finding.explanation && (
                                    <details className="mt-1">
                                      <summary className="text-xs cursor-pointer hover:underline">
                                        Regulatory Context
                                      </summary>
                                      <p className="text-xs mt-1 p-2 bg-white rounded">
                                        {finding.explanation}
                                      </p>
                                    </details>
                                  )}
                                </div>
                              </div>
                            ))}
                            {findings.length > 3 && (
                              <p className="text-xs text-gray-500 ml-2">
                                +{findings.length - 3} more {category.toLowerCase()} issues...
                              </p>
                            )}
                          </div>
                        </div>
                      ));
                    })()}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
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
    </Layout>
  );
}