// @flow
import * as React from 'react';

import type { SVGProps } from 'components/ui/Icon/internal/SVGs/types';

export default function DotsMenu(props: SVGProps): React.Element<'svg'> {
  return (
    <svg
      width="4"
      height="12"
      viewBox="0 0 4 12"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M2.00008 3.33335C2.73341 3.33335 3.33341 2.73335 3.33341 2.00002C3.33341 1.26669 2.73341 0.666687 2.00008 0.666687C1.26675 0.666687 0.666748 1.26669 0.666748 2.00002C0.666748 2.73335 1.26675 3.33335 2.00008 3.33335ZM2.00008 4.66669C1.26675 4.66669 0.666748 5.26669 0.666748 6.00002C0.666748 6.73335 1.26675 7.33335 2.00008 7.33335C2.73341 7.33335 3.33341 6.73335 3.33341 6.00002C3.33341 5.26669 2.73341 4.66669 2.00008 4.66669ZM0.666748 10C0.666748 9.26669 1.26675 8.66669 2.00008 8.66669C2.73341 8.66669 3.33341 9.26669 3.33341 10C3.33341 10.7334 2.73341 11.3334 2.00008 11.3334C1.26675 11.3334 0.666748 10.7334 0.666748 10Z"
        fill="currentColor"
      />
    </svg>
  );
}