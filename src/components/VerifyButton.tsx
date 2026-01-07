import React, { useEffect, useRef, useState } from "react";

export default function VerifyButton() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<object | null>(null);
  const [error, setError] = useState<string | null>(null);
  const hideTimerRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (hideTimerRef.current) {
        window.clearTimeout(hideTimerRef.current);
      }
    };
  }, []);

  function scheduleHide() {
    if (hideTimerRef.current) window.clearTimeout(hideTimerRef.current);
    hideTimerRef.current = window.setTimeout(() => {
      setResult(null);
      setError(null);
      hideTimerRef.current = null;
    }, 15000); // 15 seconds
  }

  async function handleVerify() {
    const token =
      window.prompt(
        "Paste a Databricks token here (leave blank to use server env):"
      ) || undefined;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("/api/genie/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, testText: "ping from UI" }),
      });

      if (!res.ok) {
        const txt = await res.text();
        setError(`Verification failed: ${res.status} ${txt}`);
        scheduleHide();
        return;
      }

      const data = await res.json();
      setResult(data);
      scheduleHide();
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(err);
      setError("Error calling verification endpoint; see console for details");
      scheduleHide();
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    if (hideTimerRef.current) window.clearTimeout(hideTimerRef.current);
    hideTimerRef.current = null;
    setResult(null);
    setError(null);
  }

  return (
    <div className="verify-root">
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <button
          className="verify-btn"
          onClick={handleVerify}
          disabled={loading}
        >
          {loading ? "Verifying..." : "Verify Genie"}
        </button>
        <button
          className="verify-clear"
          onClick={handleClear}
          disabled={loading && !result && !error}
        >
          Clear
        </button>
      </div>

      {error && <div className="verify-error">{error}</div>}

      {result && (
        <pre className="verify-result">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}
