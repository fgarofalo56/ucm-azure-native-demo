import { apiClient } from "./client";
import type { AppUser, CurrentUser, PaginatedResponse, RoleInfo } from "./types";

export async function getCurrentUser(): Promise<CurrentUser> {
  const { data } = await apiClient.get<CurrentUser>("/admin/me");
  return data;
}

export async function listUsers(
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<AppUser>> {
  const { data } = await apiClient.get<PaginatedResponse<AppUser>>(
    "/admin/users",
    { params: { page, page_size: pageSize } },
  );
  return data;
}

export async function listRoles(): Promise<RoleInfo[]> {
  const { data } = await apiClient.get<RoleInfo[]>("/admin/roles");
  return data;
}

export async function assignUserRoles(
  userId: string,
  roleNames: string[],
): Promise<AppUser> {
  const { data } = await apiClient.put<AppUser>(
    `/admin/users/${userId}/roles`,
    { role_names: roleNames },
  );
  return data;
}

// System Settings
export interface SystemSettings {
  [key: string]: {
    value: string;
    description: string | null;
    updated_at: string | null;
    updated_by: string | null;
    is_sensitive: boolean;
  };
}

export async function getSystemSettings(): Promise<SystemSettings> {
  const { data } = await apiClient.get<SystemSettings>("/admin/settings");
  return data;
}

export async function updateSystemSettings(
  updates: Record<string, string>,
): Promise<SystemSettings> {
  const { data } = await apiClient.put<SystemSettings>(
    "/admin/settings",
    updates,
  );
  return data;
}
