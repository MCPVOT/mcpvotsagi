import { useCallback, useState } from 'react';

type UseControllableStateProps<T> = {
  value?: T;
  defaultValue?: T;
  onChange?: (value: T) => void;
};

/**
 * Custom hook to handle controllable state
 * This allows components to work in both controlled and uncontrolled modes
 */
export function useControllableState<T>({
  value,
  defaultValue,
  onChange,
}: UseControllableStateProps<T>) {
  const [internalValue, setInternalValue] = useState<T | undefined>(defaultValue);

  const isControlled = value !== undefined;
  const currentValue = isControlled ? value : internalValue;

  const setValue = useCallback(
    (newValue: T | ((prev: T | undefined) => T)) => {
      const resolvedValue = typeof newValue === 'function'
        ? (newValue as (prev: T | undefined) => T)(currentValue)
        : newValue;

      if (!isControlled) {
        setInternalValue(resolvedValue);
      }

      onChange?.(resolvedValue);
    },
    [isControlled, currentValue, onChange]
  );

  return [currentValue, setValue] as const;
}
