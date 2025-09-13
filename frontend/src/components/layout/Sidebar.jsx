import { useState } from "react";
import { FileText, BarChart2, Settings, Sun, Moon } from "lucide-react";

const navItems = [
  { label: "Upload", icon: FileText, active: true },
  { label: "Results", icon: BarChart2 },
  { label: "Rules", icon: Settings },
];

export default function Sidebar() {
  const [activeItem, setActiveItem] = useState("Upload");
  const [darkMode, setDarkMode] = useState(false);
  
  const toggleTheme = () => {
    setDarkMode(!darkMode);
    // In a real app, you would apply the theme change here
    document.documentElement.classList.toggle('dark-mode');
  };

  return (
    <aside className="w-56 bg-white border-r h-screen p-4 flex flex-col justify-between">
      <div>
        <div className="mb-6 pl-3">
          <h2 className="text-lg font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            HealthTech GxP
          </h2>
        </div>
        
        <nav className="space-y-2">
          {navItems.map((item) => (
            <button
              key={item.label}
              className={`flex items-center w-full px-3 py-2 text-sm font-medium rounded-lg transition-colors
                ${activeItem === item.label 
                  ? "bg-indigo-50 text-indigo-700" 
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"}`}
              onClick={() => setActiveItem(item.label)}
            >
              <item.icon size={18} className="mr-2" />
              {item.label}
              {activeItem === item.label && (
                <span className="ml-auto h-2 w-2 rounded-full bg-indigo-500"></span>
              )}
            </button>
          ))}
        </nav>
      </div>
      
      <div className="mt-auto pt-4 border-t">
        <button
          className="flex items-center w-full px-3 py-2 text-sm font-medium rounded-lg text-gray-600 hover:bg-gray-100"
          onClick={toggleTheme}
        >
          {darkMode ? (
            <>
              <Sun size={18} className="mr-2" />
              Light Mode
            </>
          ) : (
            <>
              <Moon size={18} className="mr-2" />
              Dark Mode
            </>
          )}
        </button>
      </div>
    </aside>
  );
}