import { useState } from "react";
import { Search, FolderSearch, Loader2, Check } from "lucide-react";
import { clsx } from "clsx";
import { useInvestigations } from "../../hooks/useInvestigations";
import Modal from "./Modal";
import Button from "./Button";

interface InvestigationPickerProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (investigationId: string) => void;
  loading?: boolean;
  title?: string;
}

export default function InvestigationPicker({
  isOpen,
  onClose,
  onSelect,
  loading = false,
  title = "Add to Investigation",
}: InvestigationPickerProps) {
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const { data, isLoading } = useInvestigations(undefined, 1, search.trim() || undefined);

  const filtered = data?.data ?? [];

  const handleConfirm = () => {
    if (selected) onSelect(selected);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="md"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={!selected || loading}
            loading={loading}
          >
            Add Files
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search investigations..."
            className="form-input pl-9 w-full"
            autoFocus
          />
        </div>

        {/* Investigation list */}
        <div className="max-h-64 overflow-y-auto -mx-1 px-1">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-5 w-5 text-primary-500 animate-spin" />
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8">
              <FolderSearch className="h-8 w-8 text-secondary-300 dark:text-secondary-600" />
              <p className="mt-2 text-sm text-secondary-500 dark:text-secondary-400">
                {search ? "No matching investigations" : "No investigations found"}
              </p>
            </div>
          ) : (
            <div className="space-y-1">
              {filtered.map((inv) => (
                <button
                  key={inv.id}
                  onClick={() => setSelected(inv.id)}
                  className={clsx(
                    "flex items-center gap-3 w-full rounded-lg px-3 py-2.5 text-left transition-colors",
                    selected === inv.id
                      ? "bg-primary-50 border border-primary-300 dark:bg-primary-500/10 dark:border-primary-500/50"
                      : "hover:bg-secondary-50 border border-transparent dark:hover:bg-secondary-800/50",
                  )}
                >
                  <FolderSearch
                    className={clsx(
                      "h-4 w-4 shrink-0",
                      selected === inv.id
                        ? "text-primary-600 dark:text-primary-400"
                        : "text-secondary-400",
                    )}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-secondary-900 dark:text-secondary-100 truncate">
                      {inv.title}
                    </p>
                    <p className="text-xs text-secondary-500 dark:text-secondary-400">
                      {inv.record_id} &middot; {inv.document_count} docs
                    </p>
                  </div>
                  {selected === inv.id && (
                    <Check className="h-4 w-4 text-primary-600 dark:text-primary-400 shrink-0" />
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
}
