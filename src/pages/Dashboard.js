const ParcelMap = ({variables}) => {
  // ... rest of the code
  return (
    <div>
      {variables.map((variable) => (
        <pre>{JSON.stringify(variable)}</pre>
      ))}
    </div>
  );
};