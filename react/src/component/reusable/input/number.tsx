import React, { ChangeEventHandler } from "react";
import { Form } from "react-bootstrap";
import { SrInputBaseProps } from "./input";


export function SrNumberInput(props: SrInputBaseProps<string>) {
    let onChange: ChangeEventHandler<HTMLInputElement | HTMLTextAreaElement> = (event) => {
        props.onChange(event.target.value);
    }
    return <Form.Control size="sm" className={'text-end'} type="text" {...props} onChange={onChange}></Form.Control>
}

// dont wrap the input, wrap the data access
