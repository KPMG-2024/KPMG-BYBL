const CopyButton = ({ text }) => {
    const copyToClipboard = () => {
      navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard');
      }).catch(err => {
        console.error('Error copying text: ', err);
      });
    };
  
    return (
      <button onClick={copyToClipboard} className="ml-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded">
        복사
      </button>
    );
  };

export default CopyButton;