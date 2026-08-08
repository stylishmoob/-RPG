import { expect, request, test , type APIRequestContext, } from "@playwright/test";
import process from "node:process";

const apiBaseURL = process.env.E2E_API_URL ?? "http://127.0.0.1:8000";
const runId = crypto.randomUUID();
const testUser = {
  userName: `e2e_stopwatch_${runId}`,
  password: "test-password",
};
const categoryName = `E2E Stopwatch ${runId}`;

let categoryId: string;

async function newApiContext() {
  return request.newContext({
    baseURL: apiBaseURL,
  });
}

async function login(api: APIRequestContext, userName: string, password: string) {
  const response = await api.post("/api/login", {
    data: {
      user_name: userName,
      password,
    },
  });

  expect(response.status()).toBe(200);
}

test.describe("stopwatch", () => {
  test.beforeAll(async () => {
    const adminApi = await newApiContext();
    const userApi = await newApiContext();

    try {
      await login(adminApi, "administrator", "1111");

      const addCategoryResponse = await adminApi.post("/api/admin/categories/add", {
        data: {
          category_name: categoryName,
        },
      });
      expect(addCategoryResponse.ok()).toBeTruthy();

      const categoriesResponse = await adminApi.get("/api/admin/categories");
      expect(categoriesResponse.ok()).toBeTruthy();

      const categoriesBody = await categoriesResponse.json();
      const category = categoriesBody.MasterCategories.find(
        (masterCategory: { id: string | number; name: string }) => masterCategory.name === categoryName,
      );
      expect(category).toBeTruthy();
      categoryId = String(category.id);

      const registerResponse = await userApi.post("/api/register", {
        data: {
          user_name: testUser.userName,
          password: testUser.password,
        },
      });
      expect(registerResponse.status()).toBe(201);

      await login(userApi, testUser.userName, testUser.password);

      const addUserCategoryResponse = await userApi.post("/api/category/add", {
        data: {
          master_category_id: categoryId,
        },
      });
      expect(addUserCategoryResponse.ok()).toBeTruthy();
    } finally {
      await adminApi.dispose();
      await userApi.dispose();
    }
  });

  test.afterAll(async () => {
    const adminApi = await newApiContext();

    try {
      const loginResponse = await adminApi.post("/api/login", {
        data: {
          user_name: "administrator",
          password: "1111",
        },
      });

      if (!loginResponse.ok()) {
        return;
      }

      const usersResponse = await adminApi.get("/api/admin/users");
      if (usersResponse.ok()) {
        const usersBody = await usersResponse.json();
        const user = usersBody.users.find(
          (adminUser: { id: string; username: string }) => adminUser.username === testUser.userName,
        );

        if (user) {
          await adminApi.post("/api/admin/users/delete", {
            data: {
              user_id: user.id,
            },
          });
        }
      }

      const categoriesResponse = await adminApi.get("/api/admin/categories");
      if (categoriesResponse.ok()) {
        const categoriesBody = await categoriesResponse.json();
        const category = categoriesBody.MasterCategories.find(
          (masterCategory: { id: string | number; name: string }) => masterCategory.name === categoryName,
        );

        if (category) {
          await adminApi.post("/api/admin/categories/delete", {
            data: {
              category_id: category.id,
            },
          });
        }
      }
    } finally {
      await adminApi.dispose();
    }
  });

  test("can start, stop, and save a stopwatch log", async ({ page }) => {
    await page.goto("/login");

    await page.getByLabel("ユーザー名").fill(testUser.userName);
    await page.getByLabel("パスワード").fill(testUser.password);
    await page.getByRole("button", { name: "ログイン" }).click();

    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByText(testUser.userName, { exact: true })).toBeVisible();

    await page.getByLabel("カテゴリー").selectOption({ label: categoryName });

    await page.getByRole("button", { name: "START" }).click();
    await expect(page.getByRole("button", { name: "STOP" })).toBeVisible();
    await expect(page.getByText(/00:00:0[1-9]/)).toBeVisible({ timeout: 3_000 });

    const saveResponsePromise = page.waitForResponse(
      response =>
        response.url().includes("/api/save_action") &&
        response.request().method() === "POST",
    );

    await page.getByRole("button", { name: "STOP" }).click();

    const saveResponse = await saveResponsePromise;
    expect(saveResponse.ok()).toBeTruthy();
    await expect(saveResponse.json()).resolves.toMatchObject({
      success: true,
    });

    await expect(page.getByRole("status")).toContainText("保存しました");
    await expect(page.locator("#today-log-list")).toContainText(categoryName);
    await expect(page.getByRole("button", { name: "START" })).toBeVisible();
  });
});
