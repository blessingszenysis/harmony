// @flow
import * as React from 'react';

import type { SVGProps } from 'components/ui/Icon/internal/SVGs/types';

export default function Information(props: SVGProps): React.Element<'svg'> {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 21 21"
      height="21"
      width="21"
      {...props}
    >
      <rect fill="none" x="0" y="0" width="21" height="21" />
      <path
        fill="currentColor"
        transform="translate(3 3)"
        d="M7.5,1
	C6.7,1,6,1.7,6,2.5S6.7,4,7.5,4S9,3.3,9,2.5S8.3,1,7.5,1z M4,5v1c0,0,2,0,2,2v2c0,2-2,2-2,2v1h7v-1c0,0-2,0-2-2V6c0-0.5-0.5-1-1-1H4
	z"
        stroke="rgba(255,255,255,0.25)"
        strokeWidth="2"
      />
      <path
        fill="currentColor"
        transform="translate(3 3)"
        d="M7.5,1
	C6.7,1,6,1.7,6,2.5S6.7,4,7.5,4S9,3.3,9,2.5S8.3,1,7.5,1z M4,5v1c0,0,2,0,2,2v2c0,2-2,2-2,2v1h7v-1c0,0-2,0-2-2V6c0-0.5-0.5-1-1-1H4
	z"
      />
    </svg>
  );
}
