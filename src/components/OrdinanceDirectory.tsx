import React from 'react';

const OrdinanceDirectory = () => {
  return (
    <div className="min-h-screen bg-gray-900 p-8 flex flex-col items-center justify-center">
      <div className="w-full max-w-4xl backdrop-blur-xl bg-white/10 border-none rounded-3xl p-10 shadow-2xl stitch-design-pattern">
        <h1 className="text-4xl font-bold text-white mb-6 tracking-tight">
          Florida Ordinance Directory
        </h1>
        <div className="space-y-4">
          <div className="bg-white/5 border-none rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
            <h2 className="text-xl text-blue-200 font-semibold mb-2">Miami-Dade County</h2>
            <p className="text-gray-300">Short-Term Rental License Required: Yes</p>
          </div>
        </div>
      </div>
    </div>
  );
};
export default OrdinanceDirectory;
