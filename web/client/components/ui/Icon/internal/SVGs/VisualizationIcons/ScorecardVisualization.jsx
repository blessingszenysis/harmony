// @flow
import * as React from 'react';

import type { SVGProps } from 'components/ui/Icon/internal/SVGs/types';

export default function ScorecardVisualization(
  props: SVGProps,
): React.Element<'svg'> {
  return (
    <svg
      width="64px"
      height="64px"
      viewBox="0 0 64 64"
      color="#2D80C2"
      data-viz-icon-no-outline
      {...props}
    >
      <g fill="currentColor">
        <path
          opacity="0.1"
          d="M37.46 24.25h25c.09 0 .16.2.16.46v11c0 .26-.07.46-.16.46h-25c-.09 0-.17-.2-.17-.46v-11c0-.26.08-.46.17-.46zM12.16 50.15h25c.09 0 .16.21.16.46v11c0 .25-.07.46-.16.46h-25c-.1 0-.17-.21-.17-.46v-11c.01-.25.07-.46.17-.46z"
        />
        <path
          opacity="0.3"
          d="M12.16 12.33h25c.09 0 .16.21.16.46v11c0 .25-.07.46-.16.46h-25c-.1 0-.17-.21-.17-.46v-11c.01-.25.07-.46.17-.46zM37.46 37.2h25c.09 0 .16.21.16.46v11c0 .25-.07.46-.16.46h-25c-.09 0-.17-.21-.17-.46v-11c0-.25.08-.46.17-.46zM12.16 24.25h25c.09 0 .16.2.16.46v11c0 .26-.07.46-.16.46h-25c-.1 0-.17-.2-.17-.46v-11c.01-.26.07-.46.17-.46zM37.46 50.15h25c.09 0 .16.21.16.46v11c0 .25-.07.46-.16.46h-25c-.09 0-.17-.21-.17-.46v-11c0-.25.08-.46.17-.46z"
        />
        <path
          opacity="0.6"
          d="M37.46 12.33h25c.09 0 .16.21.16.46v11c0 .25-.07.46-.16.46h-25c-.09 0-.17-.21-.17-.46v-11c0-.25.08-.46.17-.46zM12.16 37.2h25c.09 0 .16.21.16.46v11c0 .25-.07.46-.16.46h-25c-.1 0-.17-.21-.17-.46v-11c.01-.25.07-.46.17-.46z"
        />
        <path d="M62.6 64H1.4A1.4 1.4 0 010 62.6V1.4A1.4 1.4 0 011.4 0h61.2A1.4 1.4 0 0164 1.4v61.2a1.4 1.4 0 01-1.4 1.4zM2 62h60V2H2z" />
        <path d="M1 10.33h61v2H1zM1 62h62v2H1z" />
        <path d="M36.29 11.33h2V63h-2zM62 11h2v52h-2zM10.34 11.33h2V63h-2zM0 11h2v52H0z" />
        <path d="M11.65 23.25h51.28v2H11.65zM11.65 36.16h51.28v2H11.65zM11.65 49.08h51.28v2H11.65z" />
      </g>
    </svg>
  );
}
