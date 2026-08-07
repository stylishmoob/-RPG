import { expect, request, test } from "@playwright/test";
import process from "node:process";

const apiBaseURL = process.env.E2E_API_URL ?? "http://127.0.0.1:8000";
const testUser = {
  userName: "test_user",
  password: "test-password",
};

test.describe("login", () => {
  test.beforeAll(async () => {
    const api = await request.newContext({
      baseURL: apiBaseURL,
    });

    try {
      const response = await api.post("/api/register", {
        data: {
          user_name: testUser.userName,
          password: testUser.password,
        },
      });

      expect(
        [201, 409],
        "test_user を事前登録できる、または既に存在すること",
      ).toContain(response.status());
    } finally {
      await api.dispose();
    }
  });

  test("test_user can login and see their username on home", async ({ page }) => {
    await page.goto("/login");

    await page.getByLabel("ユーザー名").fill(testUser.userName);
    await page.getByLabel("パスワード").fill(testUser.password);
    await page.getByRole("button", { name: "ログイン" }).click();

    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByText("NAME", { exact: true })).toBeVisible();
    await expect(page.getByText(testUser.userName, { exact: true })).toBeVisible();
  });
});
