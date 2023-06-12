import React, { ChangeEventHandler } from "react";
import { Form } from "react-bootstrap";
import { DataHandle } from "../../../data/handle";

export function SrNumberInput(props: { onChange: (newValue: string) => void, value: string, isInvalid: boolean }) {
    let onChange: ChangeEventHandler<HTMLInputElement | HTMLTextAreaElement> = (event) => {
        props.onChange(event.target.value);
    }
    return <Form.Control size="sm" className={'text-end'} type="text" {...props} onChange={onChange}></Form.Control>
}

const INT_REGEXP = /^[-+]?\d+$/;
const FLOAT_REGEXP = /^\s*(\-|\+)?(\d+|(\d*(\.\d*)))([eE][+-]?\d+)?\s*$/;

export const IntegerValidator = (val: string) => {
    return INT_REGEXP.test(val);
}

export const FloatValidator = (val: string) => {
    return FLOAT_REGEXP.test(val);
}

// valid if not included
export const OptionalValidator = (val: any) => {
    return val === undefined || val === null;
}

export function SrIntegerInputWrapper(props: {  }) {

}
