// @flow
import * as React from 'react';

import type { SVGProps } from 'components/ui/Icon/internal/SVGs/types';

export default function NotificationBell(
  props: SVGProps,
): React.Element<'svg'> {
  return (
    <svg
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 60 60"
      {...props}
    >
      <g clipPath="url(#clip0)" fill="#266CA5">
        <path d="M49.721 43.17a4.83 4.83 0 110 9.66H10.28a4.83 4.83 0 110-9.66H49.72zm0-1.967H10.28a6.797 6.797 0 000 13.594H49.72a6.797 6.797 0 000-13.594z" />
        <path d="M30 1.967a1.82 1.82 0 011.82 1.78 1.453 1.453 0 000 .207l-.178 1.79 1.8.335A18.845 18.845 0 0148.876 24.59v18.374l1.643.275a4.81 4.81 0 013.344 2.273v.059l.148.285.059.128c.04.08.076.162.108.245 0 .07.05.128.069.187l.078.227c0 .072.02.15.06.236v.649c.01.157.01.315 0 .472a4.81 4.81 0 01-1.27 3.423c-.445.42-.965.754-1.534.984-.292.12-.595.212-.905.275-.323.067-.653.1-.983.098H33.905l-.167 1.79a3.757 3.757 0 01-7.476 0l-.167-1.79H10.279c-.33 0-.66-.029-.984-.088a6.034 6.034 0 01-.905-.285 4.917 4.917 0 01-1.534-.984A4.81 4.81 0 015.439 48a5.027 5.027 0 010-.511v-.118-.512c.012-.073.028-.145.05-.216l.078-.227c0-.059 0-.118.069-.186l.098-.246.07-.138.147-.275-1.702-.984 1.75.915a4.791 4.791 0 013.483-2.223l1.643-.276V24.59A18.846 18.846 0 0126.556 6.08l1.78-.325-.137-1.82v-.226a1.83 1.83 0 011.8-1.74zM30 0a3.787 3.787 0 00-3.787 3.787v.354a20.843 20.843 0 00-17.056 20.45v16.72a6.738 6.738 0 00-4.692 3.178l-.068.108-.207.383-.088.187c0 .118-.109.236-.148.354-.04.118-.069.177-.098.266-.03.088-.07.206-.109.305-.039.098-.059.226-.078.334-.02.108 0 .187-.07.285-.068.099 0 .266-.058.404a1.964 1.964 0 000 .236c-.015.22-.015.44 0 .659a6.826 6.826 0 004.15 6.265 6.886 6.886 0 002.657.532h13.957a5.715 5.715 0 0011.39 0h14.026c.912 0 1.815-.18 2.656-.532a6.825 6.825 0 004.15-6.265c.016-.22.016-.44 0-.66a1.977 1.977 0 000-.235c0-.138 0-.276-.058-.404-.06-.127 0-.186-.07-.285-.068-.098-.048-.216-.078-.334-.03-.118-.069-.207-.108-.305-.04-.099-.059-.177-.098-.266-.04-.088-.099-.236-.148-.354l-.088-.187-.207-.383-.069-.108a6.738 6.738 0 00-4.76-3.177V24.59A20.843 20.843 0 0033.757 4.141v-.354A3.787 3.787 0 0030 0z" />
        <path d="M30 5.754A18.895 18.895 0 0148.875 24.59v18.384l1.643.275a4.82 4.82 0 01-.797 9.58H10.28a4.82 4.82 0 01-.797-9.55l1.643-.276V24.59A18.895 18.895 0 0130 5.754zm0-1.967A20.843 20.843 0 009.157 24.59v16.722a6.787 6.787 0 001.122 13.485H49.72a6.787 6.787 0 001.122-13.485V24.59A20.842 20.842 0 0030 3.787z" />
      </g>
      <defs>
        <clipPath id="clip0">
          <path fill="#fff" d="M0 0h60v60H0z" />
        </clipPath>
      </defs>
    </svg>
  );
}
