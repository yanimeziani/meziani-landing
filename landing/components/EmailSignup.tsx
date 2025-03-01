// components/EmailSignup.tsx
"use client";

import React, { useState, FormEvent, ChangeEvent } from "react";

const EmailSignup: React.FC = () => {
  const [email, setEmail] = useState<string>("");
  const [status, setStatus] = useState<{
    type: "success" | "error" | "";
    message: string;
  }>({ type: "", message: "" });
  const [loading, setLoading] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();

    if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
      setStatus({
        type: "error",
        message: "Please enter a valid email address",
      });
      return;
    }

    setLoading(true);
    setStatus({ type: "", message: "" });

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setStatus({
        type: "success",
        message: "Thank you for subscribing!",
      });
      setEmail("");
    } catch {
      setStatus({
        type: "error",
        message: "Something went wrong. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex flex-col sm:flex-row bg-white rounded-full overflow-hidden shadow-md">
          <input
            type="email"
            value={email}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              setEmail(e.target.value)
            }
            placeholder="Your email address"
            disabled={loading}
            className="flex-grow py-3 px-6 text-gray-800 focus:outline-none font-space-grotesk"
            aria-label="Email address"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-gray-900 text-white font-space-grotesk font-semibold py-3 px-6 transition-colors duration-300 hover:bg-blue-600 sm:m-1 sm:rounded-full disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {loading ? "Subscribing..." : "Subscribe"}
          </button>
        </div>

        {status.message && (
          <div
            className={`mt-4 py-2 px-4 rounded ${
              status.type === "success"
                ? "bg-green-100 bg-opacity-20 border-l-4 border-green-500 text-green-700"
                : "bg-red-100 bg-opacity-20 border-l-4 border-red-500 text-red-700"
            }`}
            role="alert"
          >
            {status.message}
          </div>
        )}
      </form>

      <p className="text-sm text-center text-white text-opacity-80">
        We respect your privacy and will never share your information.
      </p>
    </div>
  );
};

export default EmailSignup;
