// app/page.tsx or pages/index.tsx
import React from "react";
import Link from "next/link";
import EmailSignup from "@/components/EmailSignup";

export default function HomePage() {
  return (
    <>
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white bg-opacity-90 backdrop-blur-sm shadow-sm py-4">
        <div className="container mx-auto px-4 flex justify-between items-center">
          <div className="font-space-grotesk font-medium text-2xl text-gray-900 tracking-tight">
            「meziani」
          </div>

          <nav className="flex space-x-6">
            <a
              href="#"
              className="font-space-grotesk font-medium text-gray-800 hover:text-blue-600 transition-colors hidden sm:block"
            >
              about
            </a>
          </nav>
        </div>
      </header>

      {/* Hero Section with Email Catcher - flex-grow-1 makes it expand to fill available space */}
      <main className="flex-grow">
        <section className="py-20 md:py-32 bg-gradient-to-br from-blue-600 to-indigo-700 relative overflow-hidden min-h-[calc(100vh-8rem)]">
          {/* Background decorative circles */}
          <div className="absolute top-20 right-0 w-64 h-64 bg-white bg-opacity-5 rounded-full"></div>
          <div className="absolute -bottom-32 -left-20 w-96 h-96 bg-white bg-opacity-5 rounded-full"></div>

          <div className="container mx-auto px-4 relative z-10 h-full flex items-center">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="font-space-grotesk text-4xl md:text-6xl font-bold text-white leading-tight mb-6 tracking-tight">
                Simplify your workflow with automation.
              </h1>
              <p className="text-xl text-white text-opacity-90 mb-10">
                An innovative platform designed to help teams collaborate
                seamlessly and deliver exceptional results. Join our community
                of innovators.
              </p>

              {/* Email Catcher Component */}
              <EmailSignup />
            </div>
          </div>
        </section>
      </main>

      {/* Footer - now sticks to the bottom */}
      <footer className="bg-gray-900 text-gray-400 py-8 mt-auto">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <div className="font-space-grotesk font-medium text-xl text-white mb-2">
                「meziani」
              </div>
              <p className="text-sm">
                © {new Date().getFullYear()} 「meziani」. All rights reserved.
              </p>
            </div>

            <div className="flex space-x-8">
              <Link href="#" className="hover:text-white transition-colors">
                Privacy
              </Link>
              <Link href="#" className="hover:text-white transition-colors">
                Terms
              </Link>
              <Link
                href="mailto:mezianiyani0@gmail.com"
                className="hover:text-white transition-colors"
              >
                Contact
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}
