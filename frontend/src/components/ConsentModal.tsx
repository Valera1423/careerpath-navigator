import { useTranslation } from 'react-i18next';

interface Props {
  checked: boolean;
  onChange: (v: boolean) => void;
  onOpenTerms: () => void;
}

export function ConsentCheckbox({ checked, onChange, onOpenTerms }: Props) {
  const { t } = useTranslation('onboarding');
  return (
    <label className="consent">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span>
        {t('consent_label')}.{' '}
        <button type="button" className="link" onClick={onOpenTerms}>
          {t('consent_link')}
        </button>
      </span>
    </label>
  );
}