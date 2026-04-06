import { useState } from "react";
import {
  HelpCircle,
  BookOpen,
  FileText,
  ChevronDown,
  ExternalLink,
} from "lucide-react";
import { clsx } from "clsx";

const tabs = ["FAQ", "User Guide", "Glossary"] as const;
type Tab = (typeof tabs)[number];

const faqs: { question: string; answer: string }[] = [
  {
    question: "What is AssuranceNet?",
    answer:
      "AssuranceNet is a document management system designed for the USDA Food Safety and Inspection Service (FSIS). It provides secure storage, version tracking, and PDF conversion for investigation-related documents within an Azure-native architecture.",
  },
  {
    question: "What is FSIS?",
    answer:
      "FSIS (Food Safety and Inspection Service) is an agency of the United States Department of Agriculture responsible for ensuring the safety of the nation's commercial supply of meat, poultry, and processed egg products.",
  },
  {
    question: "How do I create an investigation?",
    answer:
      'Navigate to the Investigations page and click "New Investigation." Provide a unique Record ID (format: INVESTIGATION-XXXX), a descriptive title, and an optional description. The investigation will be created with "Active" status.',
  },
  {
    question: "How do I upload documents?",
    answer:
      "Open an investigation and use the upload area to drag & drop files or click to browse. Files up to 500MB are supported. Non-PDF documents are automatically queued for PDF conversion.",
  },
  {
    question: "What is PDF conversion?",
    answer:
      "AssuranceNet automatically converts uploaded documents (Word, Excel, images, etc.) to PDF format for standardized viewing and merging. The conversion status is tracked per document: Pending, Processing, Completed, or Failed.",
  },
  {
    question: "How do roles and permissions work?",
    answer:
      "AssuranceNet uses role-based access control (RBAC). Users are auto-provisioned as Viewers on first login. Administrators can assign roles including: Administrator (full access), Case Manager (manage investigations), Document Manager (manage documents), Reviewer (read + audit), and Viewer (read-only).",
  },
  {
    question: "How do I search for documents?",
    answer:
      "Use the search bar in the header or navigate to the Search page. You can search across investigation titles, record IDs, descriptions, and document filenames. Results are grouped by type.",
  },
  {
    question: "Where does the demo data come from?",
    answer:
      "Demo data is sourced from publicly available FSIS investigation records at fsis.usda.gov/science-data. All data used is public record and intended for demonstration purposes only.",
  },
];

const guideSteps: { title: string; content: string }[] = [
  {
    title: "1. Sign In",
    content:
      "Use your Microsoft organizational account to sign in. Your account is automatically provisioned with Viewer access on first login.",
  },
  {
    title: "2. Dashboard Overview",
    content:
      "The dashboard shows key metrics: total investigations, active cases, document counts, and pending conversions. Charts visualize document distribution and status.",
  },
  {
    title: "3. Managing Investigations",
    content:
      "Create, update, and close investigations. Each investigation has a unique Record ID, title, description, and status (Active, Closed, Archived). Filter by status using the tabs.",
  },
  {
    title: "4. Uploading Documents",
    content:
      "Upload files via drag & drop or file browser. Documents are stored in Azure Blob Storage with versioning. Non-PDF files are automatically queued for PDF conversion.",
  },
  {
    title: "5. PDF Merging",
    content:
      "Select multiple documents within an investigation and merge them into a single PDF. The merged file is generated on-demand and downloaded directly.",
  },
  {
    title: "6. File Explorer",
    content:
      "Browse the blob storage hierarchy organized by investigation. View folder structure, file sizes, and modification dates.",
  },
  {
    title: "7. Audit Log",
    content:
      "Track all system activity including document uploads, downloads, deletions, and role changes. Filter by event type, user, date range, and resource.",
  },
];

const glossary: { term: string; definition: string }[] = [
  { term: "FSIS", definition: "Food Safety and Inspection Service - USDA agency responsible for food safety oversight" },
  { term: "HACCP", definition: "Hazard Analysis Critical Control Points - systematic preventive approach to food safety" },
  { term: "NRTE", definition: "Not Ready To Eat - food products requiring further cooking before consumption" },
  { term: "STEC", definition: "Shiga toxin-producing E. coli - pathogenic bacteria found in contaminated food" },
  { term: "NRP", definition: "National Residue Program - FSIS program monitoring chemical residues in meat and poultry" },
  { term: "COA", definition: "Certificate of Analysis - document certifying analytical testing results" },
  { term: "EST", definition: "Establishment Number - unique identifier assigned to FSIS-inspected facilities" },
  { term: "SSOP", definition: "Sanitation Standard Operating Procedures - documented cleaning and sanitation protocols" },
  { term: "NOIE", definition: "Notice of Intended Enforcement - formal regulatory action notice issued by FSIS" },
  { term: "SPS", definition: "Sanitary and Phytosanitary measures - international food safety standards (WTO)" },
];

export function HelpPage() {
  const [activeTab, setActiveTab] = useState<Tab>("FAQ");
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="page-header mb-1">Help & Documentation</h2>
        <p className="page-subtitle">
          Frequently asked questions, user guide, and terminology
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-xl bg-secondary-100 dark:bg-secondary-800 p-1">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={clsx(
              "flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all",
              activeTab === tab
                ? "bg-white text-secondary-900 shadow-sm dark:bg-secondary-700 dark:text-secondary-100"
                : "text-secondary-600 hover:text-secondary-900 dark:text-secondary-400 dark:hover:text-secondary-200",
            )}
          >
            {tab === "FAQ" && <HelpCircle className="h-4 w-4" />}
            {tab === "User Guide" && <BookOpen className="h-4 w-4" />}
            {tab === "Glossary" && <FileText className="h-4 w-4" />}
            {tab}
          </button>
        ))}
      </div>

      {/* FAQ */}
      {activeTab === "FAQ" && (
        <div className="space-y-2">
          {faqs.map((faq, idx) => (
            <div
              key={faq.question}
              className={clsx(
                "rounded-xl border transition-colors",
                "border-secondary-200 dark:border-secondary-700",
                expandedFaq === idx &&
                  "bg-secondary-50/50 dark:bg-secondary-800/50",
              )}
            >
              <button
                onClick={() =>
                  setExpandedFaq(expandedFaq === idx ? null : idx)
                }
                className="flex w-full items-center justify-between px-5 py-4 text-left"
              >
                <span className="text-sm font-medium text-secondary-900 dark:text-secondary-100 pr-4">
                  {faq.question}
                </span>
                <ChevronDown
                  className={clsx(
                    "h-4 w-4 text-secondary-400 transition-transform shrink-0",
                    expandedFaq === idx && "rotate-180",
                  )}
                />
              </button>
              {expandedFaq === idx && (
                <div className="px-5 pb-4">
                  <p className="text-sm text-secondary-600 dark:text-secondary-400 leading-relaxed">
                    {faq.answer}
                  </p>
                </div>
              )}
            </div>
          ))}

          <div className="mt-4 rounded-xl bg-primary-50 dark:bg-primary-500/10 border border-primary-200 dark:border-primary-500/20 p-4">
            <p className="text-sm text-primary-700 dark:text-primary-300">
              Data sourced from{" "}
              <a
                href="https://www.fsis.usda.gov/science-data"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 font-medium underline underline-offset-2"
              >
                fsis.usda.gov/science-data
                <ExternalLink className="h-3 w-3" />
              </a>
              . This application is for demonstration purposes only.
            </p>
          </div>
        </div>
      )}

      {/* User Guide */}
      {activeTab === "User Guide" && (
        <div className="space-y-4">
          {guideSteps.map((step) => (
            <div key={step.title} className="card">
              <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100 mb-2">
                {step.title}
              </h3>
              <p className="text-sm text-secondary-600 dark:text-secondary-400 leading-relaxed">
                {step.content}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Glossary */}
      {activeTab === "Glossary" && (
        <div className="card overflow-hidden p-0">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-secondary-200 dark:border-secondary-700">
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-secondary-400">
                  Term
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-secondary-400">
                  Definition
                </th>
              </tr>
            </thead>
            <tbody>
              {glossary.map((item) => (
                <tr
                  key={item.term}
                  className="border-b border-secondary-100 dark:border-secondary-800 last:border-0"
                >
                  <td className="px-6 py-3">
                    <span className="text-sm font-semibold text-secondary-900 dark:text-secondary-100">
                      {item.term}
                    </span>
                  </td>
                  <td className="px-6 py-3">
                    <span className="text-sm text-secondary-600 dark:text-secondary-400">
                      {item.definition}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
