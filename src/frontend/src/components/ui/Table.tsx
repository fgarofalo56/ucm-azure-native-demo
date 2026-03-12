import type { ReactNode } from "react";
import { clsx } from "clsx";
import { Inbox } from "lucide-react";

interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => ReactNode;
  className?: string;
  sortable?: boolean;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T) => string;
  emptyMessage?: string;
  emptyIcon?: ReactNode;
  onRowClick?: (item: T) => void;
  loading?: boolean;
}

export default function Table<T>({
  columns,
  data,
  keyExtractor,
  emptyMessage = "No data available",
  emptyIcon,
  onRowClick,
  loading = false,
}: TableProps<T>) {
  if (loading) {
    return (
      <div className="table-wrapper">
        <div className="flex flex-col items-center justify-center py-16">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
          <p className="mt-3 text-sm text-secondary-500 dark:text-secondary-400">
            Loading...
          </p>
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="table-wrapper">
        <div className="flex flex-col items-center justify-center py-16">
          {emptyIcon || (
            <div className="rounded-xl bg-secondary-100 dark:bg-secondary-800 p-4">
              <Inbox className="h-8 w-8 text-secondary-400 dark:text-secondary-500" />
            </div>
          )}
          <p className="mt-4 text-sm font-medium text-secondary-500 dark:text-secondary-400">
            {emptyMessage}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="min-w-full divide-y divide-secondary-200 dark:divide-secondary-700">
        <thead className="table-header">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className={clsx("table-header-cell", col.className)}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="table-body">
          {data.map((item) => (
            <tr
              key={keyExtractor(item)}
              onClick={() => onRowClick?.(item)}
              className={clsx("table-row", onRowClick && "cursor-pointer")}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={clsx("table-cell", col.className)}
                >
                  {col.render
                    ? col.render(item)
                    : ((item as Record<string, unknown>)[col.key] as ReactNode)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
