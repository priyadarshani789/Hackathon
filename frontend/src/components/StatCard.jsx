export default function StatCard({ title, value, subtitle, icon, loading, highlight, warning }) {
  return (
    <div className=" p-2 mt-10 text-center">Analyze</div>
    // <div className={`flex flex-col p-4 bg-white rounded-xl shadow-sm border card-hover-effect transition-all
    //   ${highlight ? 'border-blue-200' : ''}
    //   ${warning ? 'border-yellow-300 bg-yellow-50' : ''}`}
    // >
    //   <div className="flex items-center justify-between">
    //     <h2 className="text-sm text-gray-500 font-medium">{title}</h2>
    //     {icon && (
    //       <span className={`
    //         ${highlight && !warning ? 'text-blue-500' : ''}
    //         ${warning ? 'text-yellow-500' : 'text-gray-400'}
    //       `}>
    //         {icon}
    //       </span>
    //     )}
    //   </div>
    //   <p className={`text-2xl font-bold mt-2 
    //     ${warning ? 'text-yellow-600' : 'text-gray-800'}
    //     ${highlight && !warning ? 'text-blue-700' : ''}`}>
    //     {loading ? 
    //       <span className="flex items-center">
    //         <span className="animate-pulse">{value}</span>
    //         <span className="ml-2 h-2 w-2 bg-blue-500 rounded-full animate-ping"></span>
    //       </span> : value}
    //   </p>
    //   <p className="text-xs text-gray-400">{subtitle}</p>
    // </div>
  );
}