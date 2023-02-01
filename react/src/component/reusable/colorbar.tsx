import React from 'react';
import { DynamicAxis } from "./axis";
import { Range1d } from '../../types';
import { Scale } from '@visx/visx';
import { createColorScale } from "../../utility/component";

type ColorBarProps = {
    range: Range1d,
    height: number,
    colorMap: string,
}

export function ColorBar({ range, height, colorMap }: ColorBarProps) {
    const colorbarScale = createColorScale({ min: 0, max: 1} , colorMap);
    const width = 30;
    return (
        <>
            {
                Array.from(Array(height).keys()).map(y => (
                    <rect
                        key={`colorBar${y}`}
                        width={width}
                        height="1"
                        y={y}
                        fill={colorbarScale(1 - y / height) as string}
                    >
                    </rect>
                ))
            }
            <g transform={`translate(${width}, 0)`}>
                <DynamicAxis
                    orientation='right'
                    scale={
                        Scale.scaleLinear({
                            domain: [range.min, range.max],
                            range: [height, 0],
                        })
                    }
                    graphSize={height}
                />
            </g>
        </>
    );
}
