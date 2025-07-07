'use client';
import { ClerkProvider } from '@clerk/nextjs';
import { dark } from '@clerk/themes';
import { useTheme } from 'next-themes';
import React from 'react';
import { ActiveThemeProvider } from '../active-theme';

export default function Providers({
  activeThemeValue,
  children
}: {
  activeThemeValue: string;
  children: React.ReactNode;
}) {
  // we need the resolvedTheme value to set the baseTheme for clerk based on the dark or light theme
  const { resolvedTheme } = useTheme();

  // Check if we have valid Clerk keys or if Clerk is disabled
  const clerkPublishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  const isClerkEnabled = clerkPublishableKey &&
    clerkPublishableKey !== 'pk_test_demo_key_for_development' &&
    !clerkPublishableKey.includes('demo');

  return (
    <>
      <ActiveThemeProvider initialTheme={activeThemeValue}>
        {isClerkEnabled ? (
          <ClerkProvider
            appearance={{
              baseTheme: resolvedTheme === 'dark' ? dark : undefined
            }}
          >
            {children}
          </ClerkProvider>
        ) : (
          // Render children without Clerk when disabled/demo mode
          children
        )}
      </ActiveThemeProvider>
    </>
  );
}
