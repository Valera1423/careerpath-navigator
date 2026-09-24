import { expect, test } from '@playwright/test';

const USER_ID = `e2e-${Date.now()}`;

test.describe('CareerPath happy path', () => {
  test.beforeEach(async ({ context }) => {
    // Симулируем dev-пользователя (ALLOW_INSECURE_INIT_DATA=true на backend)
    await context.addInitScript((id) => {
      (window as unknown as { __DEV_USER_ID?: string }).__DEV_USER_ID = id;
    }, USER_ID);
  });

  test('онбординг → план → отметка шага → отклик', async ({ page }) => {
    await page.goto('/');

    // Онбординг
    await expect(page.getByText('Кем хочешь стать?')).toBeVisible();
    await page.getByPlaceholder('Например: Аналитик данных').fill('Аналитик данных');
    await page.getByRole('button', { name: 'Далее' }).click();

    await expect(page.getByText('Твой опыт')).toBeVisible();
    await page.getByRole('button', { name: 'Далее' }).click();

    await expect(page.getByText('Что уже умеешь?')).toBeVisible();
    await page.getByText('excel', { exact: true }).click();
    await page.getByText('python', { exact: true }).click();

    // Согласие 152-ФЗ
    await page.getByRole('checkbox').check();
    await page.getByRole('button', { name: 'Построить план' }).click();

    // Дашборд
    await expect(page.getByText('готовность к роли')).toBeVisible({ timeout: 15_000 });

    // Переходим в план
    await page.getByRole('button', { name: 'План' }).click();
    const firstStep = page.locator('.step').first();
    await expect(firstStep).toBeVisible();
    await firstStep.click();

    // Прогресс увеличился
    await page.getByRole('button', { name: 'Обзор' }).click();
    await expect(page.locator('.progress__bar')).not.toHaveCSS('width', '0px');
  });

  test('симулятор интервью проходится до конца', async ({ page }) => {
    await page.goto('/');

    // Быстрый онбординг (если нужно)
    const needsOnboarding = await page.getByText('Кем хочешь стать?').isVisible().catch(() => false);
    if (needsOnboarding) {
      await page.getByPlaceholder('Например: Аналитик данных').fill('Аналитик данных');
      await page.getByRole('button', { name: 'Далее' }).click();
      await page.getByRole('button', { name: 'Далее' }).click();
      await page.getByRole('checkbox').check();
      await page.getByRole('button', { name: 'Построить план' }).click();
    }

    await page.getByRole('button', { name: 'Интервью' }).click();
    await page.getByRole('button', { name: 'Начать' }).click();

    const answer = 'Когда я работал над проектом, нужно было ускорить отчёты. Я написал скрипт, в итоге время сократилось в 3 раза.';
    for (let i = 0; i < 5; i++) {
      await page.getByPlaceholder(/Ваш ответ/).fill(answer);
      await page.getByRole('button', { name: 'Ответить' }).click();
      await page.waitForTimeout(500);
    }

    await expect(page.getByText('Сессия завершена')).toBeVisible({ timeout: 15_000 });
  });
});