export default function Header() {
  return (
    <header className="flex items-center justify-between px-6 py-3 border-b bg-white">
      <div>
        <h1 className="text-xl font-bold">Compliance Assistant</h1>
        <p className="text-sm text-gray-500">HealthTech Document Validation</p>
      </div>
      <span className="px-3 py-1 text-sm rounded-full bg-green-100 text-green-700">
        GxP Validated
      </span>
    </header>
  );
}
