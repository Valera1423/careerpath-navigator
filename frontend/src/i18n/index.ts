import i18n from 'i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import { initReactI18next } from 'react-i18next';

import ruCommon from './ru/common.json';
import ruOnboarding from './ru/onboarding.json';
import ruDashboard from './ru/dashboard.json';
import ruPlan from './ru/plan.json';
import ruVacancies from './ru/vacancies.json';
import ruSettings from './ru/settings.json';
import ruLegal from './ru/legal.json';
import enCommon from './en/common.json';
import enOnboarding from './en/onboarding.json';
import enDashboard from './en/dashboard.json';
import enPlan from './en/plan.json';
import enVacancies from './en/vacancies.json';
import enSettings from './en/settings.json';
import enLegal from './en/legal.json';

void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'ru',
    supportedLngs: ['ru', 'en'],
    ns: ['common', 'onboarding', 'dashboard', 'plan', 'vacancies', 'settings', 'legal'],
    defaultNS: 'common',
    interpolation: { escapeValue: false },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'careerpath.lang',
    },
    resources: {
      ru: {
        common: ruCommon,
        onboarding: ruOnboarding,
        dashboard: ruDashboard,
        plan: ruPlan,
        vacancies: ruVacancies,
        settings: ruSettings,
        legal: ruLegal,
      },
      en: {
        common: enCommon,
        onboarding: enOnboarding,
        dashboard: enDashboard,
        plan: enPlan,
        vacancies: enVacancies,
        settings: enSettings,
        legal: enLegal,
      },
    },
  });

export default i18n;