package com.fakenews.server.domain.post.controller;

import com.fakenews.server.domain.post.dto.PostRegisterReqDto;
import com.fakenews.server.domain.post.dto.PostReadResDto;
import com.fakenews.server.domain.post.dto.PostRegisterResDto;
import com.fakenews.server.domain.post.service.PostService;
import lombok.RequiredArgsConstructor;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;

import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
public class PostController {

    private final PostService postService;

    @PostMapping({"/api/posts", "/post/register"})
    @ResponseStatus(HttpStatus.CREATED)
    public PostRegisterResDto register(@Valid @RequestBody PostRegisterReqDto postRegisterReqDto,
                                       Authentication authentication){

        return postService.register(postRegisterReqDto, authentication.getName());
    }

    @GetMapping({"/api/posts/{postId}", "/post/{postId}"})
    public PostReadResDto read(@PathVariable Long postId){
        return postService.read(postId);
    }

}
